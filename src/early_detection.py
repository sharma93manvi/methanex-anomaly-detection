"""
Early detection analysis module
"""

import pandas as pd
import numpy as np
from src.config import EARLY_WARNING_LOOKBACK_HOURS


def identify_anomaly_periods(df, anomaly_col='anomaly_combined'):
    """
    Identify continuous anomaly periods
    
    Args:
        df: DataFrame with anomaly flags
        anomaly_col: Name of anomaly flag column
        
    Returns:
        List of tuples (start_idx, end_idx) for each anomaly period
    """
    if anomaly_col not in df.columns:
        return []
    
    anomaly_periods = []
    in_anomaly = False
    start_idx = None
    
    for i, is_anomaly in enumerate(df[anomaly_col]):
        if is_anomaly and not in_anomaly:
            # Start of new anomaly period
            start_idx = i
            in_anomaly = True
        elif not is_anomaly and in_anomaly:
            # End of anomaly period
            anomaly_periods.append((start_idx, i - 1))
            in_anomaly = False
    
    # Handle case where anomaly continues to end of data
    if in_anomaly:
        anomaly_periods.append((start_idx, len(df) - 1))
    
    return anomaly_periods


def find_early_indicators(df, anomaly_periods, lookback_hours=EARLY_WARNING_LOOKBACK_HOURS):
    """
    Find which sensors flagged earliest before each anomaly period
    
    Args:
        df: DataFrame with sensor data and anomaly flags
        anomaly_periods: List of (start_idx, end_idx) tuples
        lookback_hours: How many hours to look back
        
    Returns:
        Dictionary with early indicator analysis
    """
    early_indicators = []
    
    # Get all anomaly flag columns (excluding combined flags)
    anomaly_cols = [col for col in df.columns if col.startswith('anomaly_') and 
                   col not in ['anomaly_combined', 'anomaly_statistical', 'anomaly_ml', 
                              'anomaly_score_statistical', 'anomaly_score_ml']]
    
    for start_idx, end_idx in anomaly_periods:
        # Look back from start of anomaly
        lookback_start = max(0, start_idx - lookback_hours)
        lookback_end = start_idx
        
        period_info = {
            'anomaly_start': df.iloc[start_idx]['Timestamp'] if 'Timestamp' in df.columns else start_idx,
            'anomaly_end': df.iloc[end_idx]['Timestamp'] if 'Timestamp' in df.columns else end_idx,
            'duration_hours': end_idx - start_idx + 1,
            'early_indicators': {}
        }
        
        # Check which sensors flagged first
        for col in anomaly_cols:
            if col in df.columns:
                # Find first flag in lookback period
                lookback_data = df.iloc[lookback_start:lookback_end]
                lookback_flags = lookback_data[col]
                flagged_mask = lookback_flags == True
                
                if flagged_mask.any():
                    # Get the first index where flag is True
                    first_flag_pos = lookback_data.index[flagged_mask][0]
                    hours_before = start_idx - (first_flag_pos - df.index[0])
                    period_info['early_indicators'][col] = {
                        'first_flag_hours_before': hours_before,
                        'flag_count': int(lookback_flags.sum())
                    }
        
        early_indicators.append(period_info)
    
    return early_indicators


def rank_sensors_by_early_warning(early_indicators):
    """
    Rank sensors by their early warning capability
    
    Args:
        early_indicators: List of early indicator dictionaries
        
    Returns:
        DataFrame with sensor rankings
    """
    sensor_stats = {}
    
    for period_info in early_indicators:
        for sensor, info in period_info['early_indicators'].items():
            if sensor not in sensor_stats:
                sensor_stats[sensor] = {
                    'total_periods': 0,
                    'total_lead_time': 0,
                    'min_lead_time': float('inf'),
                    'max_lead_time': 0,
                    'flag_count': 0
                }
            
            sensor_stats[sensor]['total_periods'] += 1
            lead_time = info['first_flag_hours_before']
            sensor_stats[sensor]['total_lead_time'] += lead_time
            sensor_stats[sensor]['min_lead_time'] = min(sensor_stats[sensor]['min_lead_time'], lead_time)
            sensor_stats[sensor]['max_lead_time'] = max(sensor_stats[sensor]['max_lead_time'], lead_time)
            sensor_stats[sensor]['flag_count'] += info['flag_count']
    
    # Calculate averages
    rankings = []
    for sensor, stats in sensor_stats.items():
        avg_lead_time = stats['total_lead_time'] / stats['total_periods'] if stats['total_periods'] > 0 else 0
        rankings.append({
            'sensor': sensor,
            'periods_detected': stats['total_periods'],
            'avg_lead_time_hours': avg_lead_time,
            'min_lead_time_hours': stats['min_lead_time'] if stats['min_lead_time'] != float('inf') else 0,
            'max_lead_time_hours': stats['max_lead_time'],
            'total_flags': stats['flag_count']
        })
    
    rankings_df = pd.DataFrame(rankings)
    rankings_df = rankings_df.sort_values('avg_lead_time_hours', ascending=False)
    
    return rankings_df


def analyze_early_detection(df, asset='Asset 1'):
    """
    Complete early detection analysis
    
    Args:
        df: DataFrame with anomaly flags
        asset: 'Asset 1' or 'Asset 2'
        
    Returns:
        Dictionary with early detection results
    """
    print(f"\n=== Early Detection Analysis for {asset} ===")
    
    # Identify anomaly periods
    anomaly_periods = identify_anomaly_periods(df, anomaly_col='anomaly_combined')
    print(f"Found {len(anomaly_periods)} anomaly periods")
    
    if len(anomaly_periods) == 0:
        print("No anomalies detected - skipping early detection analysis")
        return {
            'anomaly_periods': [],
            'early_indicators': [],
            'sensor_rankings': pd.DataFrame()
        }
    
    # Find early indicators
    early_indicators = find_early_indicators(df, anomaly_periods)
    print(f"Analyzed early indicators for {len(early_indicators)} periods")
    
    # Rank sensors
    sensor_rankings = rank_sensors_by_early_warning(early_indicators)
    print(f"Ranked {len(sensor_rankings)} sensors by early warning capability")
    
    if len(sensor_rankings) > 0:
        print("\nTop 5 early warning sensors:")
        print(sensor_rankings.head(5).to_string())
    
    return {
        'anomaly_periods': anomaly_periods,
        'early_indicators': early_indicators,
        'sensor_rankings': sensor_rankings
    }

