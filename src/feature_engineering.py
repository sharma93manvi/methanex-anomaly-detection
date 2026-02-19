"""
Feature engineering module
"""

import pandas as pd
import numpy as np
from src.config import ROLLING_WINDOW_SHORT, ROLLING_WINDOW_LONG


def compute_residuals(df, asset='Asset 1'):
    """
    Compute residuals: HP Discharge Pressure - Target Value
    
    Args:
        df: DataFrame with sensor data
        asset: 'Asset 1' or 'Asset 2'
        
    Returns:
        DataFrame with residual column added
    """
    if asset == 'Asset 1':
        pressure_col = 'Asset 1 HP - Disch Press Value'
    else:  # Asset 2
        pressure_col = 'Asset 2 - Disch Press Value'
    
    target_col = 'target Value'
    
    df = df.copy()
    df['residual'] = df[pressure_col] - df[target_col]
    
    return df


def compute_rate_of_change(df, columns=None):
    """
    Compute rate of change (first derivative) for specified columns
    
    Args:
        df: DataFrame with sensor data
        columns: List of column names to compute rate of change for
        
    Returns:
        DataFrame with rate of change columns added
    """
    df = df.copy()
    
    if columns is None:
        # Default: compute for key sensors
        columns = [
            'Asset 1 HP - Disch Press Value',
            'Asset 1 HP - Pressure & Ratio Value',
            'Asset 1T - Speed Value',
            'Asset 1T Steam Inlet flow Value',
            'Asset 2 - Disch Press Value',
            'Asset 2 Pressure & Ratio Value',
            'Asset 2T - Speed Value',
            'Asset 2T Steam Inlet flow Value'
        ]
        # Only include columns that exist and are numeric
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        columns = [col for col in columns if col in df.columns and col in numeric_cols]
    
    for col in columns:
        if col in df.columns and df[col].dtype in [np.number, 'float64', 'int64']:
            df[f'{col}_roc'] = df[col].diff()
    
    return df


def compute_rolling_statistics(df, columns=None, windows=None):
    """
    Compute rolling statistics (mean, std, min, max) for specified columns
    
    Args:
        df: DataFrame with sensor data
        columns: List of column names to compute rolling stats for
        windows: List of window sizes (in hours)
        
    Returns:
        DataFrame with rolling statistics columns added
    """
    df = df.copy()
    
    if windows is None:
        windows = [ROLLING_WINDOW_SHORT, ROLLING_WINDOW_LONG]
    
    if columns is None:
        # Default: compute for key sensors
        columns = [
            'Asset 1 HP - Disch Press Value',
            'Asset 1 HP - Pressure & Ratio Value',
            'Asset 1T - Speed Value',
            'residual',
            'Asset 2 - Disch Press Value',
            'Asset 2 Pressure & Ratio Value',
            'Asset 2T - Speed Value'
        ]
        # Only include columns that exist and are numeric
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        columns = [col for col in columns if col in df.columns and col in numeric_cols]
    
    for col in columns:
        for window in windows:
            df[f'{col}_rolling_mean_{window}h'] = df[col].rolling(window=window, min_periods=1).mean()
            df[f'{col}_rolling_std_{window}h'] = df[col].rolling(window=window, min_periods=1).std()
            df[f'{col}_rolling_min_{window}h'] = df[col].rolling(window=window, min_periods=1).min()
            df[f'{col}_rolling_max_{window}h'] = df[col].rolling(window=window, min_periods=1).max()
    
    return df


def add_time_features(df):
    """
    Add time-based features (hour, day of week, month)
    
    Args:
        df: DataFrame with Timestamp column
        
    Returns:
        DataFrame with time features added
    """
    df = df.copy()
    
    if 'Timestamp' not in df.columns:
        if df.index.name == 'Timestamp':
            df = df.reset_index()
        else:
            raise ValueError("Timestamp column not found")
    
    df['hour'] = df['Timestamp'].dt.hour
    df['day_of_week'] = df['Timestamp'].dt.dayofweek
    df['month'] = df['Timestamp'].dt.month
    df['day_of_year'] = df['Timestamp'].dt.dayofyear
    
    return df


def normalize_features(df, columns=None):
    """
    Normalize features using z-score normalization
    
    Args:
        df: DataFrame with features
        columns: List of columns to normalize (None = all numeric)
        
    Returns:
        Tuple of (normalized_df, normalization_params)
    """
    df = df.copy()
    
    if columns is None:
        # Exclude timestamp and time features
        exclude_cols = ['Timestamp', 'hour', 'day_of_week', 'month', 'day_of_year']
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        columns = [col for col in numeric_cols if col not in exclude_cols]
    
    normalization_params = {}
    
    for col in columns:
        if col in df.columns:
            mean = df[col].mean()
            std = df[col].std()
            
            if std > 0:
                df[f'{col}_normalized'] = (df[col] - mean) / std
                normalization_params[col] = {'mean': mean, 'std': std}
    
    return df, normalization_params


def engineer_features(df, asset='Asset 1'):
    """
    Complete feature engineering pipeline
    
    Args:
        df: DataFrame with sensor data
        asset: 'Asset 1' or 'Asset 2'
        
    Returns:
        DataFrame with engineered features
    """
    print(f"\n=== Feature Engineering for {asset} ===")
    
    # Compute residuals
    df = compute_residuals(df, asset=asset)
    print("✓ Computed residuals")
    
    # Compute rate of change
    df = compute_rate_of_change(df)
    print("✓ Computed rate of change features")
    
    # Compute rolling statistics
    df = compute_rolling_statistics(df)
    print("✓ Computed rolling statistics")
    
    # Add time features
    df = add_time_features(df)
    print("✓ Added time-based features")
    
    # Normalize features (for ML models)
    df, norm_params = normalize_features(df)
    print("✓ Normalized features")
    
    print(f"Final feature count: {len(df.columns)}")
    
    return df

