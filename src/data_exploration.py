"""
Data exploration and cleaning module
"""

import pandas as pd
import numpy as np
from src.config import ASSET1_SPEED_THRESHOLD, ASSET1_FLOW_THRESHOLD, ASSET2_SPEED_THRESHOLD, ASSET2_FLOW_THRESHOLD


def load_and_validate_data(filepath):
    """
    Load CSV data and perform basic validation
    
    Args:
        filepath: Path to the CSV file
        
    Returns:
        DataFrame with validated data
    """
    print("Loading data...")
    df = pd.read_csv(filepath)
    
    # Parse timestamps
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
    df = df.sort_values('Timestamp').reset_index(drop=True)
    
    # Clean numeric columns - convert non-numeric values to NaN
    numeric_cols = df.select_dtypes(include=[object]).columns
    for col in numeric_cols:
        if col != 'Timestamp':
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    print(f"Data shape: {df.shape}")
    print(f"Time range: {df['Timestamp'].min()} to {df['Timestamp'].max()}")
    
    # Check sampling rate
    dt = df['Timestamp'].diff().dt.total_seconds().dropna()
    print(f"Median time step: {dt.median()} seconds ({dt.median()/3600:.1f} hours)")
    if len(dt.mode()) > 0:
        print(f"Most common time step: {dt.mode()[0]} seconds")
    
    return df


def assess_data_quality(df):
    """
    Assess data quality: missing values, constant sensors, outliers
    
    Args:
        df: DataFrame with sensor data
        
    Returns:
        Dictionary with quality metrics
    """
    print("\n=== Data Quality Assessment ===")
    
    # Missing values
    missing = df.isna().sum()
    missing_pct = (missing / len(df)) * 100
    print(f"\nMissing values:")
    print(missing_pct[missing_pct > 0].sort_values(ascending=False))
    
    # Constant/flatlined sensors
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    constant_sensors = []
    for col in numeric_cols:
        if df[col].nunique() <= 1:
            constant_sensors.append(col)
    
    if constant_sensors:
        print(f"\nConstant/flatlined sensors: {constant_sensors}")
    else:
        print("\nNo constant sensors detected")
    
    # Outliers using IQR method (for reference, not removing)
    outlier_info = {}
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outliers = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
        outlier_info[col] = {
            'count': outliers,
            'pct': (outliers / len(df)) * 100
        }
    
    print(f"\nOutliers (IQR method) - Top 5 sensors:")
    outlier_df = pd.DataFrame(outlier_info).T.sort_values('pct', ascending=False).head(5)
    print(outlier_df)
    
    return {
        'missing': missing_pct,
        'constant_sensors': constant_sensors,
        'outlier_info': outlier_info
    }


def remove_duplicates(df):
    """
    Remove duplicate timestamps
    
    Args:
        df: DataFrame with sensor data
        
    Returns:
        DataFrame with duplicates removed
    """
    initial_count = len(df)
    df = df.drop_duplicates(subset='Timestamp', keep='first')
    removed = initial_count - len(df)
    
    if removed > 0:
        print(f"\nRemoved {removed} duplicate timestamps")
    else:
        print("\nNo duplicate timestamps found")
    
    return df


def identify_unplanned_outages(df, asset='Asset 1'):
    """
    Identify unplanned outages (non-operating periods)
    
    Args:
        df: DataFrame with sensor data
        asset: 'Asset 1' or 'Asset 2'
        
    Returns:
        DataFrame with is_unplanned_outage flag column added
    """
    if asset == 'Asset 1':
        speed_col = 'Asset 1T - Speed Value'
        flow_col = 'Asset 1T Steam Inlet flow Value'
        speed_threshold = ASSET1_SPEED_THRESHOLD
        flow_threshold = ASSET1_FLOW_THRESHOLD
    else:  # Asset 2
        speed_col = 'Asset 2T - Speed Value'
        flow_col = 'Asset 2T Steam Inlet flow Value'
        speed_threshold = ASSET2_SPEED_THRESHOLD
        flow_threshold = ASSET2_FLOW_THRESHOLD
    
    # Non-operating criteria: Speed <= threshold AND Flow <= threshold
    # These are treated as unplanned outages
    is_outage = (df[speed_col] <= speed_threshold) & (df[flow_col] <= flow_threshold)
    
    df = df.copy()
    df['is_unplanned_outage'] = is_outage
    
    outage_count = is_outage.sum()
    print(f"\n=== Unplanned Outage Identification for {asset} ===")
    print(f"Total records: {len(df)}")
    print(f"Unplanned outage records: {outage_count} ({outage_count/len(df)*100:.1f}%)")
    print(f"Operating records: {len(df) - outage_count} ({(len(df) - outage_count)/len(df)*100:.1f}%)")
    
    return df


def filter_operating_periods(df, asset='Asset 1'):
    """
    Filter data to only operating periods
    
    Args:
        df: DataFrame with sensor data
        asset: 'Asset 1' or 'Asset 2'
        
    Returns:
        DataFrame filtered to operating periods
    """
    print(f"\n=== Filtering Operating Periods for {asset} ===")
    
    if asset == 'Asset 1':
        speed_col = 'Asset 1T - Speed Value'
        flow_col = 'Asset 1T Steam Inlet flow Value'
        speed_threshold = ASSET1_SPEED_THRESHOLD
        flow_threshold = ASSET1_FLOW_THRESHOLD
    else:  # Asset 2
        speed_col = 'Asset 2T - Speed Value'
        flow_col = 'Asset 2T Steam Inlet flow Value'
        speed_threshold = ASSET2_SPEED_THRESHOLD
        flow_threshold = ASSET2_FLOW_THRESHOLD
    
    # Operating criteria: Speed > threshold OR Flow > threshold
    operating = (df[speed_col] > speed_threshold) | (df[flow_col] > flow_threshold)
    
    df_operating = df[operating].copy()
    
    print(f"Total records: {len(df)}")
    print(f"Operating records: {len(df_operating)} ({len(df_operating)/len(df)*100:.1f}%)")
    print(f"Non-operating records: {len(df) - len(df_operating)}")
    
    return df_operating


def resample_data(df, freq='1H'):
    """
    Resample data to consistent frequency (if needed)
    
    Args:
        df: DataFrame with sensor data
        freq: Target frequency (default: 1 hour)
        
    Returns:
        Resampled DataFrame
    """
    df = df.set_index('Timestamp')
    
    # Resample numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df_resampled = df[numeric_cols].resample(freq).mean()
    
    # Forward fill any gaps
    df_resampled = df_resampled.ffill()
    
    df_resampled = df_resampled.reset_index()
    
    return df_resampled


def prepare_data(filepath):
    """
    Complete data preparation pipeline
    
    Args:
        filepath: Path to CSV file
        
    Returns:
        Tuple of (df_asset1, df_asset2, quality_metrics)
        Note: DataFrames now include both operating periods and unplanned outages
        with is_unplanned_outage flag column
    """
    # Load and validate
    df = load_and_validate_data(filepath)
    
    # Assess quality
    quality_metrics = assess_data_quality(df)
    
    # Remove duplicates
    df = remove_duplicates(df)
    
    # Identify unplanned outages and add flag column (includes all data)
    df_asset1 = identify_unplanned_outages(df, asset='Asset 1')
    df_asset2 = identify_unplanned_outages(df, asset='Asset 2')
    
    # Note: We now return all data (operating + outages) instead of filtering
    # This allows ML models to train on both operating and outage periods
    # The is_unplanned_outage flag can be used to distinguish them
    
    # Resample if needed (check for gaps)
    # For now, assuming data is already hourly - can add resampling if gaps detected
    
    return df_asset1, df_asset2, quality_metrics

