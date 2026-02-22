"""
Model Manager - Handles model persistence and inference
Saves and loads trained models for reuse on new data
"""

import pickle
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

from src.feature_engineering import engineer_features
from src.statistical_detection import detect_anomalies_statistical
from src.ml_detection import detect_anomalies_ml, prepare_ml_features
from src.early_detection import analyze_early_detection
from src.config import TRAIN_SPLIT, ISOLATION_FOREST_CONTAMINATION, ANOMALY_SCORE_PERCENTILE


class ModelManager:
    """
    Manages model persistence and inference on new data
    """
    
    def __init__(self, model_dir="models"):
        """
        Initialize ModelManager
        
        Args:
            model_dir: Directory to save/load models
        """
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        
        self.models = {}
        self.scalers = {}
        self.feature_cols = {}
        self.normalization_params = {}
        self.early_detection_history = {}
        self.sensor_rankings = {}
        
    def save_models(self, df_asset1, df_asset2, early_detection_asset1=None, early_detection_asset2=None):
        """
        Train and save models for both assets
        
        Args:
            df_asset1: Processed DataFrame for Asset 1
            df_asset2: Processed DataFrame for Asset 2
            early_detection_asset1: Early detection results for Asset 1
            early_detection_asset2: Early detection results for Asset 2
        """
        print("\n=== Saving Models ===")
        
        for asset_name, df in [('Asset 1', df_asset1), ('Asset 2', df_asset2)]:
            print(f"\nSaving models for {asset_name}...")
            
            # Prepare features
            X, feature_cols = prepare_ml_features(df)
            self.feature_cols[asset_name] = feature_cols
            
            # Split data
            split_idx = int(len(X) * TRAIN_SPLIT)
            X_train = X[:split_idx]
            
            # Train and save scaler
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            scaler_path = self.model_dir / f"{asset_name.replace(' ', '_')}_scaler.pkl"
            joblib.dump(scaler, scaler_path)
            self.scalers[asset_name] = scaler
            print(f"  ✓ Saved scaler: {scaler_path}")
            
            # Train and save Isolation Forest
            from sklearn.ensemble import IsolationForest
            iso_forest = IsolationForest(
                contamination=ISOLATION_FOREST_CONTAMINATION,
                random_state=42,
                n_estimators=100
            )
            iso_forest.fit(X_train_scaled)
            
            model_path = self.model_dir / f"{asset_name.replace(' ', '_')}_isolation_forest.pkl"
            joblib.dump(iso_forest, model_path)
            self.models[asset_name] = {'isolation_forest': iso_forest}
            print(f"  ✓ Saved Isolation Forest: {model_path}")
            
            # Save early detection history and sensor rankings (in memory and to disk)
            if asset_name == 'Asset 1' and early_detection_asset1:
                self.early_detection_history[asset_name] = early_detection_asset1
                if len(early_detection_asset1.get('sensor_rankings', [])) > 0:
                    self.sensor_rankings[asset_name] = early_detection_asset1['sensor_rankings']
            elif asset_name == 'Asset 2' and early_detection_asset2:
                self.early_detection_history[asset_name] = early_detection_asset2
                if len(early_detection_asset2.get('sensor_rankings', [])) > 0:
                    self.sensor_rankings[asset_name] = early_detection_asset2['sensor_rankings']
        
        # Persist sensor_rankings and early_detection_history to disk for load_models()
        for asset_name in ['Asset 1', 'Asset 2']:
            asset_key = asset_name.replace(' ', '_')
            if asset_name in self.sensor_rankings and self.sensor_rankings[asset_name] is not None:
                rank_path = self.model_dir / f"{asset_key}_sensor_rankings.pkl"
                with open(rank_path, 'wb') as f:
                    pickle.dump(self.sensor_rankings[asset_name], f)
                print(f"  ✓ Saved sensor rankings: {rank_path}")
            if asset_name in self.early_detection_history and self.early_detection_history[asset_name]:
                hist_path = self.model_dir / f"{asset_key}_early_detection.pkl"
                with open(hist_path, 'wb') as f:
                    pickle.dump(self.early_detection_history[asset_name], f)
                print(f"  ✓ Saved early detection: {hist_path}")
        
        # Save metadata
        metadata = {
            'feature_cols': self.feature_cols,
            'model_version': '1.0'
        }
        metadata_path = self.model_dir / "metadata.pkl"
        with open(metadata_path, 'wb') as f:
            pickle.dump(metadata, f)
        print(f"\n✓ Saved metadata: {metadata_path}")
        
    def load_models(self):
        """
        Load saved models from disk.
        Supports two formats:
        1. train_models.py format: metadata.pkl + Asset_1/Asset_2 *.pkl
        2. Notebook/ml_detection format: asset_1/asset_2 *_isolation_forest*.joblib
        """
        print("\n=== Loading Models ===")
        
        # Try format 1: metadata.pkl + .pkl files (from train_models.py)
        metadata_path = self.model_dir / "metadata.pkl"
        if metadata_path.exists():
            return self._load_models_pkl(metadata_path)
        
        # Try format 2: .joblib files (from notebook / ml_detection pipeline)
        if self._load_models_joblib():
            return True
        
        print("  ⚠ No saved models found. Models need to be trained first.")
        return False
    
    def _load_models_pkl(self, metadata_path):
        """Load models saved by train_models.py (metadata.pkl + .pkl)."""
        with open(metadata_path, 'rb') as f:
            metadata = pickle.load(f)
        self.feature_cols = metadata.get('feature_cols', {})
        print(f"  ✓ Loaded metadata (version: {metadata.get('model_version', 'unknown')})")
        
        for asset_name in ['Asset_1', 'Asset_2']:
            asset_display = asset_name.replace('_', ' ')
            scaler_path = self.model_dir / f"{asset_name}_scaler.pkl"
            if scaler_path.exists():
                self.scalers[asset_display] = joblib.load(scaler_path)
                print(f"  ✓ Loaded scaler for {asset_display}")
            model_path = self.model_dir / f"{asset_name}_isolation_forest.pkl"
            if model_path.exists():
                iso_forest = joblib.load(model_path)
                if asset_display not in self.models:
                    self.models[asset_display] = {}
                self.models[asset_display]['isolation_forest'] = iso_forest
                print(f"  ✓ Loaded Isolation Forest for {asset_display}")
        
        for asset_name in ['Asset_1', 'Asset_2']:
            asset_display = asset_name.replace('_', ' ')
            rank_path = self.model_dir / f"{asset_name}_sensor_rankings.pkl"
            if rank_path.exists():
                with open(rank_path, 'rb') as f:
                    self.sensor_rankings[asset_display] = pickle.load(f)
                print(f"  ✓ Loaded sensor rankings for {asset_display}")
            hist_path = self.model_dir / f"{asset_name}_early_detection.pkl"
            if hist_path.exists():
                with open(hist_path, 'rb') as f:
                    self.early_detection_history[asset_display] = pickle.load(f)
                print(f"  ✓ Loaded early detection history for {asset_display}")
        
        return True
    
    def _load_models_joblib(self):
        """Load models saved by notebook/ml_detection (asset_*_isolation_forest*.joblib)."""
        loaded_any = False
        for asset_key, asset_display in [('asset_1', 'Asset 1'), ('asset_2', 'Asset 2')]:
            model_path = self.model_dir / f"{asset_key}_isolation_forest.joblib"
            scaler_path = self.model_dir / f"{asset_key}_isolation_forest_scaler.joblib"
            features_path = self.model_dir / f"{asset_key}_isolation_forest_features.joblib"
            if not model_path.exists() or not scaler_path.exists():
                continue
            iso_forest = joblib.load(model_path)
            scaler = joblib.load(scaler_path)
            if asset_display not in self.models:
                self.models[asset_display] = {}
            self.models[asset_display]['isolation_forest'] = iso_forest
            self.scalers[asset_display] = scaler
            if features_path.exists():
                self.feature_cols[asset_display] = joblib.load(features_path)
            else:
                self.feature_cols[asset_display] = []
            print(f"  ✓ Loaded Isolation Forest (joblib) for {asset_display}")
            loaded_any = True
        return loaded_any
    
    def predict_on_new_data(self, df_new, asset_name='Asset 1'):
        """
        Run inference on new data using saved models
        
        Args:
            df_new: New DataFrame with sensor data (must have Timestamp)
            asset_name: 'Asset 1' or 'Asset 2'
            
        Returns:
            Dictionary with predictions and anomaly flags
        """
        if asset_name not in self.models:
            raise ValueError(f"Models not loaded for {asset_name}. Call load_models() first.")
        
        print(f"\n=== Running Inference on New Data for {asset_name} ===")
        
        # Feature engineering
        df_processed = engineer_features(df_new.copy(), asset=asset_name)
        
        # Statistical detection
        df_processed = detect_anomalies_statistical(df_processed.copy(), asset=asset_name)
        
        # Prepare ML features
        X, feature_cols = prepare_ml_features(df_processed)
        
        # Check if feature columns match
        expected_cols = self.feature_cols.get(asset_name, [])
        if set(feature_cols) != set(expected_cols):
            print(f"  ⚠ Warning: Feature columns don't match exactly. Using available features.")
            # Use intersection of available features
            common_cols = list(set(feature_cols) & set(expected_cols))
            if len(common_cols) == 0:
                raise ValueError("No common features found between new data and trained model.")
            X = df_processed[common_cols].values
            X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
        else:
            X = df_processed[expected_cols].values
            X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
        
        # Scale features
        scaler = self.scalers[asset_name]
        X_scaled = scaler.transform(X)
        
        # Get predictions from Isolation Forest
        iso_forest = self.models[asset_name]['isolation_forest']
        scores = iso_forest.score_samples(X_scaled)
        
        # Convert to 0-1 scale
        scores_normalized = 1 - (scores - scores.min()) / (scores.max() - scores.min() + 1e-10)
        
        # Flag anomalies
        threshold = np.percentile(scores_normalized, ANOMALY_SCORE_PERCENTILE)
        anomaly_flags = scores_normalized >= threshold
        
        # Add to dataframe
        df_processed['anomaly_score_ml'] = scores_normalized
        df_processed['anomaly_ml'] = anomaly_flags
        
        # Combine with statistical detection
        if 'anomaly_statistical' in df_processed.columns:
            df_processed['anomaly_combined'] = df_processed['anomaly_statistical'] | df_processed['anomaly_ml']
        else:
            df_processed['anomaly_combined'] = df_processed['anomaly_ml']
        
        # Combined score
        if 'anomaly_score_statistical' in df_processed.columns:
            df_processed['anomaly_score_combined'] = (
                df_processed['anomaly_score_statistical'] + df_processed['anomaly_score_ml']
            ) / 2
        else:
            df_processed['anomaly_score_combined'] = df_processed['anomaly_score_ml']
        
        print(f"  ✓ Processed {len(df_processed)} records")
        print(f"  ✓ Detected {anomaly_flags.sum()} anomalies ({anomaly_flags.sum()/len(df_processed)*100:.2f}%)")
        
        return df_processed
    
    def get_sensor_rankings(self, asset_name='Asset 1'):
        """
        Get sensor rankings for early detection
        
        Args:
            asset_name: 'Asset 1' or 'Asset 2'
            
        Returns:
            DataFrame with sensor rankings or None
        """
        return self.sensor_rankings.get(asset_name)
    
    def get_early_detection_history(self, asset_name='Asset 1'):
        """
        Get early detection history
        
        Args:
            asset_name: 'Asset 1' or 'Asset 2'
            
        Returns:
            Dictionary with early detection history or None
        """
        return self.early_detection_history.get(asset_name)

