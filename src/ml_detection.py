"""
Machine learning-based anomaly detection methods

Model Selection Rationale:
---------------------------
After exploring multiple anomaly detection approaches, we selected Isolation Forest as the primary
ML method for the following reasons:

1. **Isolation Forest** (Selected - Primary Method):
   - Fast training and inference (seconds vs minutes for deep learning)
   - No external dependencies beyond scikit-learn
   - Effective for high-dimensional sensor data
   - Works well with engineered features (rolling stats, residuals, etc.)
   - Interpretable results
   - Proven track record in industrial anomaly detection

2. **Autoencoder** (Optional - Experimental):
   - Can capture complex non-linear patterns
   - Requires TensorFlow (large dependency, ~2GB)
   - Slow training (50 epochs, several minutes)
   - May provide marginal improvement over Isolation Forest
   - Status: Available if TensorFlow installed, but not required

3. **LSTM** (Optional - Experimental):
   - Designed for temporal sequences
   - However, our statistical methods (rolling windows, rate of change) already capture temporal patterns
   - Requires TensorFlow and significant training time
   - Status: Available if TensorFlow installed, but redundant with statistical methods

Decision: Isolation Forest + Statistical Methods provides the best balance of:
- Performance (fast, effective)
- Simplicity (no heavy dependencies)
- Interpretability (important for industrial operations)
- Maintainability (easier to debug and tune)
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from src.config import (
    TRAIN_SPLIT, ISOLATION_FOREST_CONTAMINATION,
    AUTOENCODER_EPOCHS, AUTOENCODER_BATCH_SIZE,
    LSTM_EPOCHS, LSTM_BATCH_SIZE, ANOMALY_SCORE_PERCENTILE
)

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    # Test that TensorFlow actually works (not just installed)
    _ = tf.__version__
    TENSORFLOW_AVAILABLE = True
except (ImportError, Exception) as e:
    # Catch both ImportError and runtime crashes (e.g., mutex lock issues on macOS)
    TENSORFLOW_AVAILABLE = False
    # Only print warning if it's an ImportError (not a runtime crash)
    if isinstance(e, ImportError):
        print("Warning: TensorFlow not available. Autoencoder and LSTM methods will be skipped.")
    # For runtime crashes, silently fail (common on macOS with certain Python versions)


def prepare_ml_features(df):
    """
    Prepare features for ML models
    
    Args:
        df: DataFrame with engineered features
        
    Returns:
        Feature matrix (numpy array)
    """
    # Select numeric columns (exclude timestamp, time features, anomaly flags, and outage flag)
    exclude_cols = ['Timestamp', 'hour', 'day_of_week', 'month', 'day_of_year']
    exclude_cols += [col for col in df.columns if col.startswith('anomaly')]
    exclude_cols += ['is_unplanned_outage']  # Exclude outage flag (it's a label, not a feature)
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    feature_cols = [col for col in numeric_cols if col not in exclude_cols]
    
    # Remove columns with all NaN or infinite values
    valid_cols = []
    for col in feature_cols:
        if df[col].notna().sum() > 0 and np.isfinite(df[col]).all():
            valid_cols.append(col)
    
    X = df[valid_cols].values
    
    # Handle any remaining NaN or inf values
    X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
    
    return X, valid_cols


def isolation_forest_detection(df):
    """
    Detect anomalies using Isolation Forest
    Now includes unplanned outages in training data
    
    Args:
        df: DataFrame with engineered features (includes operating periods and outages)
        
    Returns:
        Array of anomaly scores (0-1, where 1 = more anomalous)
    """
    print("  Training Isolation Forest...")
    
    X, feature_cols = prepare_ml_features(df)
    
    # Split data for training (includes both operating periods and unplanned outages)
    split_idx = int(len(X) * TRAIN_SPLIT)
    X_train = X[:split_idx]
    
    # Log training data composition if outage flag exists
    if 'is_unplanned_outage' in df.columns:
        train_outages = df.iloc[:split_idx]['is_unplanned_outage'].sum()
        train_operating = split_idx - train_outages
        print(f"    Training data: {train_operating} operating, {train_outages} unplanned outages")
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_scaled = scaler.transform(X)
    
    # Train Isolation Forest on all training data (operating + outages)
    # This helps the model learn what anomalous/unplanned outage patterns look like
    iso_forest = IsolationForest(
        contamination=ISOLATION_FOREST_CONTAMINATION,
        random_state=42,
        n_estimators=100
    )
    iso_forest.fit(X_train_scaled)
    
    # Get anomaly scores (negative scores = anomalies, more negative = more anomalous)
    scores = iso_forest.score_samples(X_scaled)
    
    # Convert to 0-1 scale (1 = most anomalous)
    scores_normalized = 1 - (scores - scores.min()) / (scores.max() - scores.min() + 1e-10)
    
    return scores_normalized


def build_autoencoder(input_dim, encoding_dim=32):
    """
    Build autoencoder model
    
    Args:
        input_dim: Number of input features
        encoding_dim: Dimension of encoded representation
        
    Returns:
        Autoencoder model
    """
    input_layer = layers.Input(shape=(input_dim,))
    
    # Encoder
    encoded = layers.Dense(encoding_dim * 2, activation='relu')(input_layer)
    encoded = layers.Dense(encoding_dim, activation='relu')(encoded)
    
    # Decoder
    decoded = layers.Dense(encoding_dim * 2, activation='relu')(encoded)
    decoded = layers.Dense(input_dim, activation='linear')(decoded)
    
    autoencoder = keras.Model(input_layer, decoded)
    autoencoder.compile(optimizer='adam', loss='mse')
    
    return autoencoder


def autoencoder_detection(df):
    """
    Detect anomalies using Autoencoder
    Now includes unplanned outages in training data
    
    Args:
        df: DataFrame with engineered features (includes operating periods and outages)
        
    Returns:
        Array of anomaly scores (0-1, where 1 = more anomalous)
    """
    if not TENSORFLOW_AVAILABLE:
        print("  Skipping Autoencoder (TensorFlow not available)")
        return np.zeros(len(df))
    
    print("  Training Autoencoder...")
    
    X, feature_cols = prepare_ml_features(df)
    input_dim = X.shape[1]
    
    # Split data for training (includes both operating periods and unplanned outages)
    split_idx = int(len(X) * TRAIN_SPLIT)
    X_train = X[:split_idx]
    
    # Log training data composition if outage flag exists
    if 'is_unplanned_outage' in df.columns:
        train_outages = df.iloc[:split_idx]['is_unplanned_outage'].sum()
        train_operating = split_idx - train_outages
        print(f"    Training data: {train_operating} operating, {train_outages} unplanned outages")
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_scaled = scaler.transform(X)
    
    # Build and train autoencoder
    autoencoder = build_autoencoder(input_dim, encoding_dim=min(32, input_dim // 2))
    
    # Train on all training data (operating + outages)
    # This helps the model learn what anomalous/unplanned outage patterns look like
    autoencoder.fit(
        X_train_scaled, X_train_scaled,
        epochs=AUTOENCODER_EPOCHS,
        batch_size=AUTOENCODER_BATCH_SIZE,
        verbose=0,
        validation_split=0.2
    )
    
    # Calculate reconstruction error
    X_pred = autoencoder.predict(X_scaled, verbose=0)
    reconstruction_error = np.mean((X_scaled - X_pred) ** 2, axis=1)
    
    # Normalize to 0-1 scale
    scores_normalized = (reconstruction_error - reconstruction_error.min()) / (
        reconstruction_error.max() - reconstruction_error.min() + 1e-10
    )
    
    return scores_normalized


def build_lstm_model(input_shape, n_features):
    """
    Build LSTM forecasting model
    
    Args:
        input_shape: Shape of input sequences
        n_features: Number of features
        
    Returns:
        LSTM model
    """
    model = keras.Sequential([
        layers.LSTM(50, return_sequences=True, input_shape=input_shape),
        layers.LSTM(50, return_sequences=False),
        layers.Dense(25),
        layers.Dense(n_features)
    ])
    
    model.compile(optimizer='adam', loss='mse')
    return model


def lstm_detection(df, sequence_length=24):
    """
    Detect anomalies using LSTM forecasting
    Now includes unplanned outages in training data
    
    Args:
        df: DataFrame with engineered features (includes operating periods and outages)
        sequence_length: Length of input sequences (hours)
        
    Returns:
        Array of anomaly scores (0-1, where 1 = more anomalous)
    """
    if not TENSORFLOW_AVAILABLE:
        print("  Skipping LSTM (TensorFlow not available)")
        return np.zeros(len(df))
    
    print("  Training LSTM...")
    
    X, feature_cols = prepare_ml_features(df)
    n_features = X.shape[1]
    
    # Create sequences
    sequences = []
    targets = []
    
    for i in range(sequence_length, len(X)):
        sequences.append(X[i-sequence_length:i])
        targets.append(X[i])
    
    sequences = np.array(sequences)
    targets = np.array(targets)
    
    if len(sequences) == 0:
        print("  Not enough data for LSTM sequences")
        return np.zeros(len(df))
    
    # Split data (includes both operating periods and unplanned outages)
    split_idx = int(len(sequences) * TRAIN_SPLIT)
    X_train_seq = sequences[:split_idx]
    y_train = targets[:split_idx]
    
    # Log training data composition if outage flag exists
    if 'is_unplanned_outage' in df.columns:
        # Count outages in training sequences (approximate)
        train_outages = df.iloc[sequence_length:sequence_length+split_idx]['is_unplanned_outage'].sum()
        train_operating = split_idx - train_outages
        print(f"    Training data: {train_operating} operating, {train_outages} unplanned outages")
    
    # Scale features
    scaler = StandardScaler()
    X_train_flat = X_train_seq.reshape(-1, n_features)
    X_train_scaled_flat = scaler.fit_transform(X_train_flat)
    X_train_scaled = X_train_scaled_flat.reshape(X_train_seq.shape)
    
    # Scale targets
    y_train_scaled = scaler.transform(y_train)
    
    # Build and train LSTM
    input_shape = (sequence_length, n_features)
    lstm_model = build_lstm_model(input_shape, n_features)
    
    lstm_model.fit(
        X_train_scaled, y_train_scaled,
        epochs=LSTM_EPOCHS,
        batch_size=LSTM_BATCH_SIZE,
        verbose=0,
        validation_split=0.2
    )
    
    # Predict and calculate residuals
    X_all_flat = sequences.reshape(-1, n_features)
    X_all_scaled_flat = scaler.transform(X_all_flat)
    X_all_scaled = X_all_scaled_flat.reshape(sequences.shape)
    
    predictions_scaled = lstm_model.predict(X_all_scaled, verbose=0)
    predictions = scaler.inverse_transform(predictions_scaled)
    
    # Calculate prediction error
    prediction_errors = np.mean((targets - predictions) ** 2, axis=1)
    
    # Pad with zeros for initial sequence_length points
    scores = np.zeros(len(df))
    scores[sequence_length:] = prediction_errors
    
    # Normalize to 0-1 scale
    if scores.max() > scores.min():
        scores_normalized = (scores - scores.min()) / (scores.max() - scores.min() + 1e-10)
    else:
        scores_normalized = scores
    
    return scores_normalized


def ensemble_scoring(df, scores_dict):
    """
    Combine scores from multiple ML methods
    
    Primary method: Isolation Forest (weight: 1.0 if alone, or 0.7 if ensemble)
    Optional methods: Autoencoder, LSTM (weight: 0.15 each if available)
    
    Args:
        df: DataFrame
        scores_dict: Dictionary of method names and scores
        
    Returns:
        Ensemble score (0-1)
    """
    # Weight different methods - Isolation Forest is primary
    # If only Isolation Forest available: weight = 1.0
    # If ensemble available: Isolation Forest = 0.7, others = 0.15 each
    base_weights = {
        'isolation_forest': 0.7,  # Primary method
        'autoencoder': 0.15,       # Optional/experimental
        'lstm': 0.15              # Optional/experimental
    }
    
    # If only Isolation Forest is available, use it exclusively
    if 'isolation_forest' in scores_dict and len(scores_dict) == 1:
        return scores_dict['isolation_forest']
    
    # Otherwise, use weighted ensemble
    ensemble_score = np.zeros(len(df))
    total_weight = 0
    
    for method, scores in scores_dict.items():
        if method in base_weights and len(scores) == len(df):
            weight = base_weights[method]
            ensemble_score += weight * scores
            total_weight += weight
    
    if total_weight > 0:
        ensemble_score = ensemble_score / total_weight
    
    return ensemble_score


def detect_anomalies_ml(df, asset='Asset 1'):
    """
    Run ML-based anomaly detection methods
    
    Primary Method: Isolation Forest (always runs)
    Optional Methods: Autoencoder, LSTM (only if TensorFlow available)
    
    Args:
        df: DataFrame with engineered features
        asset: 'Asset 1' or 'Asset 2'
        
    Returns:
        DataFrame with ML anomaly scores and flags
    """
    print(f"\n=== ML-Based Anomaly Detection for {asset} ===")
    print("Primary Method: Isolation Forest")
    if not TENSORFLOW_AVAILABLE:
        print("Note: Autoencoder and LSTM skipped (TensorFlow not available)")
        print("      Isolation Forest + Statistical methods provide comprehensive detection")
    
    df = df.copy()
    
    scores_dict = {}
    
    # 1. Isolation Forest (Primary Method - Always runs)
    try:
        iso_scores = isolation_forest_detection(df)
        df['anomaly_score_isolation_forest'] = iso_scores
        scores_dict['isolation_forest'] = iso_scores
        print("✓ Isolation Forest (Primary)")
    except Exception as e:
        print(f"✗ Isolation Forest failed: {e}")
        df['anomaly_score_isolation_forest'] = 0.0
    
    # 2. Autoencoder (Optional - Experimental, requires TensorFlow)
    if TENSORFLOW_AVAILABLE:
        try:
            ae_scores = autoencoder_detection(df)
            df['anomaly_score_autoencoder'] = ae_scores
            scores_dict['autoencoder'] = ae_scores
            print("✓ Autoencoder (Optional)")
        except Exception as e:
            print(f"✗ Autoencoder failed: {e}")
            df['anomaly_score_autoencoder'] = 0.0
    else:
        df['anomaly_score_autoencoder'] = 0.0
    
    # 3. LSTM (Optional - Experimental, requires TensorFlow)
    if TENSORFLOW_AVAILABLE:
        try:
            lstm_scores = lstm_detection(df)
            df['anomaly_score_lstm'] = lstm_scores
            scores_dict['lstm'] = lstm_scores
            print("✓ LSTM (Optional)")
        except Exception as e:
            print(f"✗ LSTM failed: {e}")
            df['anomaly_score_lstm'] = 0.0
    else:
        df['anomaly_score_lstm'] = 0.0
    
    # Ensemble scoring
    ensemble_score = ensemble_scoring(df, scores_dict)
    df['anomaly_score_ml'] = ensemble_score
    
    # 70-30 temporal split: threshold from training 70% only, then apply to full series
    split_idx = int(len(df) * TRAIN_SPLIT)
    train_scores = ensemble_score[:split_idx]
    threshold = np.percentile(train_scores, ANOMALY_SCORE_PERCENTILE)
    df['anomaly_ml'] = ensemble_score >= threshold
    
    # Mark holdout (test) set for reporting
    df['is_holdout'] = np.arange(len(df)) >= split_idx
    
    # Full-series metrics
    n_full = len(df)
    n_anom_full = int(df['anomaly_ml'].sum())
    pct_full = (n_anom_full / n_full) * 100 if n_full else 0
    
    # Holdout (last 30%) metrics
    holdout = df['is_holdout']
    n_holdout = holdout.sum()
    n_anom_holdout = int(df.loc[holdout, 'anomaly_ml'].sum())
    pct_holdout = (n_anom_holdout / n_holdout) * 100 if n_holdout else 0
    
    print(f"✓ Ensemble ML detection (threshold from training 70% only: {threshold:.3f})")
    print(f"  Full series: {n_anom_full} anomalies ({pct_full:.2f}% of {n_full} records)")
    print(f"  Holdout (last 30%): {n_anom_holdout} anomalies ({pct_holdout:.2f}% of {n_holdout} records)")
    
    return df

