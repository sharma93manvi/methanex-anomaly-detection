"""
Severity Classifier - Classifies anomaly severity levels
"""

import pandas as pd
import numpy as np


def classify_severity(anomaly_score, sensor_deviations=None, historical_severity=None):
    """
    Classify anomaly severity
    
    Args:
        anomaly_score: Anomaly score (0-1)
        sensor_deviations: Dictionary of sensor deviations (optional)
        historical_severity: Historical severity patterns (optional)
        
    Returns:
        Dictionary with:
        - severity_level: 'Low', 'Medium', 'High', 'Critical'
        - severity_score: Numeric score (0-1)
        - factors: List of contributing factors
        - color: Color code for UI
    """
    # Base severity classification on anomaly score
    if anomaly_score < 0.3:
        base_level = 'Low'
        base_score = anomaly_score / 0.3
    elif anomaly_score < 0.5:
        base_level = 'Low'
        base_score = 0.3 + (anomaly_score - 0.3) / 0.2 * 0.2
    elif anomaly_score < 0.7:
        base_level = 'Medium'
        base_score = 0.5 + (anomaly_score - 0.5) / 0.2 * 0.2
    elif anomaly_score < 0.9:
        base_level = 'High'
        base_score = 0.7 + (anomaly_score - 0.7) / 0.2 * 0.2
    else:
        base_level = 'Critical'
        base_score = 0.9 + (anomaly_score - 0.9) / 0.1 * 0.1
    
    factors = []
    
    # Adjust based on sensor deviations
    if sensor_deviations:
        num_deviated_sensors = len([d for d in sensor_deviations.values() if d > 2.0])
        
        if num_deviated_sensors >= 5:
            # Multiple sensors affected - increase severity
            if base_level == 'Low':
                base_level = 'Medium'
            elif base_level == 'Medium':
                base_level = 'High'
            elif base_level == 'High':
                base_level = 'Critical'
            factors.append(f"{num_deviated_sensors} sensors showing deviations")
        
        # Check for extreme deviations
        max_deviation = max(sensor_deviations.values()) if sensor_deviations.values() else 0
        if max_deviation > 4.0:
            if base_level != 'Critical':
                base_level = 'High' if base_level == 'Medium' else 'Critical'
            factors.append(f"Extreme deviation detected (Z-score: {max_deviation:.1f})")
    
    # Color mapping
    color_map = {
        'Low': '#10B981',      # Green
        'Medium': '#F59E0B',   # Orange
        'High': '#EF4444',     # Red
        'Critical': '#991B1B'  # Dark Red
    }
    
    return {
        'severity_level': base_level,
        'severity_score': min(1.0, base_score),
        'factors': factors if factors else ['Anomaly score based classification'],
        'color': color_map[base_level]
    }


def classify_severity_from_dataframe(df, anomaly_col='anomaly_score_combined'):
    """
    Classify severity for all rows in dataframe
    
    Args:
        df: DataFrame with anomaly scores
        anomaly_col: Column name with anomaly scores
        
    Returns:
        DataFrame with severity columns added
    """
    df = df.copy()
    
    if anomaly_col not in df.columns:
        df['severity_level'] = 'Low'
        df['severity_score'] = 0.0
        return df
    
    # Calculate sensor deviations if possible
    sensor_cols = [col for col in df.columns if 'Asset' in col and 'Value' in col]
    
    severity_levels = []
    severity_scores = []
    
    for idx, row in df.iterrows():
        anomaly_score = row[anomaly_col]
        
        # Calculate sensor deviations for this row
        sensor_deviations = {}
        if len(sensor_cols) > 0:
            for col in sensor_cols:
                if col in df.columns and pd.notna(row[col]):
                    mean_val = df[col].mean()
                    std_val = df[col].std()
                    if std_val > 0:
                        z_score = abs((row[col] - mean_val) / std_val)
                        sensor_deviations[col] = z_score
        
        result = classify_severity(anomaly_score, sensor_deviations)
        severity_levels.append(result['severity_level'])
        severity_scores.append(result['severity_score'])
    
    df['severity_level'] = severity_levels
    df['severity_score'] = severity_scores
    
    return df

