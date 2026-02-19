"""
Statistical anomaly detection methods
"""

import pandas as pd
import numpy as np
from src.config import (
    ROLLING_WINDOW_LONG, Z_SCORE_THRESHOLD, SUSTAINED_ANOMALY_DURATION,
    PERCENTILE_LOW, PERCENTILE_HIGH
)


def rolling_zscore_detection(df, column, window=ROLLING_WINDOW_LONG, threshold=Z_SCORE_THRESHOLD):
    """
    Detect anomalies using rolling z-scores
    
    Args:
        df: DataFrame with sensor data
        column: Column name to analyze
        window: Rolling window size (hours)
        threshold: Z-score threshold
        
    Returns:
        Series with anomaly flags
    """
    rolling_mean = df[column].rolling(window=window, min_periods=1).mean()
    rolling_std = df[column].rolling(window=window, min_periods=1).std()
    
    # Avoid division by zero
    rolling_std = rolling_std.replace(0, np.nan)
    
    z_scores = (df[column] - rolling_mean) / rolling_std
    z_scores = z_scores.fillna(0)
    
    anomalies = np.abs(z_scores) > threshold
    
    return anomalies, z_scores


def residual_based_detection(df, window=ROLLING_WINDOW_LONG, threshold=Z_SCORE_THRESHOLD):
    """
    Detect anomalies based on residual (HP Discharge - Target)
    
    Args:
        df: DataFrame with residual column
        window: Rolling window size
        threshold: Z-score threshold
        
    Returns:
        Series with anomaly flags
    """
    if 'residual' not in df.columns:
        raise ValueError("Residual column not found. Run feature engineering first.")
    
    anomalies, z_scores = rolling_zscore_detection(
        df, 'residual', window=window, threshold=threshold
    )
    
    return anomalies, z_scores


def moving_average_envelope_detection(df, column, window=ROLLING_WINDOW_LONG, k=3):
    """
    Detect anomalies using moving average envelopes
    
    Args:
        df: DataFrame with sensor data
        column: Column name to analyze
        window: Rolling window size
        k: Multiplier for standard deviation
        
    Returns:
        Series with anomaly flags
    """
    rolling_mean = df[column].rolling(window=window, min_periods=1).mean()
    rolling_std = df[column].rolling(window=window, min_periods=1).std()
    
    upper_bound = rolling_mean + k * rolling_std
    lower_bound = rolling_mean - k * rolling_std
    
    anomalies = (df[column] > upper_bound) | (df[column] < lower_bound)
    
    return anomalies


def percentile_based_detection(df, column, low_percentile=PERCENTILE_LOW, high_percentile=PERCENTILE_HIGH):
    """
    Detect anomalies using percentile thresholds
    
    Args:
        df: DataFrame with sensor data
        column: Column name to analyze
        low_percentile: Lower percentile threshold
        high_percentile: Upper percentile threshold
        
    Returns:
        Series with anomaly flags
    """
    low_threshold = df[column].quantile(low_percentile / 100)
    high_threshold = df[column].quantile(high_percentile / 100)
    
    anomalies = (df[column] < low_threshold) | (df[column] > high_threshold)
    
    return anomalies


def require_sustained_anomalies(anomaly_flags, duration=SUSTAINED_ANOMALY_DURATION):
    """
    Require anomalies to be sustained for a minimum duration
    
    Args:
        anomaly_flags: Boolean series of anomaly flags
        duration: Minimum duration in hours
        
    Returns:
        Series with sustained anomaly flags
    """
    # Use rolling sum to count consecutive anomalies
    rolling_sum = anomaly_flags.rolling(window=duration, min_periods=1).sum()
    sustained = rolling_sum >= duration
    
    return sustained


def detect_anomalies_statistical(df, asset='Asset 1'):
    """
    Run all statistical anomaly detection methods
    
    Args:
        df: DataFrame with engineered features
        asset: 'Asset 1' or 'Asset 2'
        
    Returns:
        DataFrame with anomaly flags and scores
    """
    print(f"\n=== Statistical Anomaly Detection for {asset} ===")
    
    df = df.copy()
    
    # Key sensors to monitor
    if asset == 'Asset 1':
        key_sensors = [
            'Asset 1 HP - Disch Press Value',
            'Asset 1 HP - Pressure & Ratio Value',
            'Asset 1T - Speed Value',
            'residual'
        ]
    else:  # Asset 2
        key_sensors = [
            'Asset 2 - Disch Press Value',
            'Asset 2 Pressure & Ratio Value',
            'Asset 2T - Speed Value'
        ]
    
    # Only use sensors that exist
    key_sensors = [s for s in key_sensors if s in df.columns]
    
    # Initialize anomaly score (will be aggregated)
    df['anomaly_score_statistical'] = 0.0
    
    # 1. Residual-based detection
    if 'residual' in df.columns:
        residual_anomalies, residual_z = residual_based_detection(df)
        df['anomaly_residual'] = residual_anomalies
        df['anomaly_score_statistical'] += residual_anomalies.astype(int)
        print("✓ Residual-based detection")
    
    # 2. Rolling z-score for each key sensor
    for sensor in key_sensors:
        if sensor in df.columns:
            anomalies, z_scores = rolling_zscore_detection(df, sensor)
            df[f'anomaly_zscore_{sensor.replace(" ", "_").replace("-", "_")}'] = anomalies
            df['anomaly_score_statistical'] += anomalies.astype(int)
    
    print("✓ Rolling z-score detection")
    
    # 3. Moving average envelope
    for sensor in key_sensors:
        if sensor in df.columns:
            anomalies = moving_average_envelope_detection(df, sensor)
            df[f'anomaly_envelope_{sensor.replace(" ", "_").replace("-", "_")}'] = anomalies
            df['anomaly_score_statistical'] += anomalies.astype(int)
    
    print("✓ Moving average envelope detection")
    
    # 4. Percentile-based detection
    for sensor in key_sensors:
        if sensor in df.columns:
            anomalies = percentile_based_detection(df, sensor)
            df[f'anomaly_percentile_{sensor.replace(" ", "_").replace("-", "_")}'] = anomalies
            df['anomaly_score_statistical'] += anomalies.astype(int)
    
    print("✓ Percentile-based detection")
    
    # Normalize score to 0-1 range
    max_score = df['anomaly_score_statistical'].max()
    if max_score > 0:
        df['anomaly_score_statistical'] = df['anomaly_score_statistical'] / max_score
    
    # Require sustained anomalies
    df['anomaly_statistical'] = require_sustained_anomalies(
        df['anomaly_score_statistical'] > 0.3  # Threshold for flagging
    )
    
    print(f"✓ Detected {df['anomaly_statistical'].sum()} sustained anomalies")
    
    return df

