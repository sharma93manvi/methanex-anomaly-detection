"""
Lead Time Predictor - Predicts how far in advance anomalies will occur
"""

import pandas as pd
import numpy as np
from src.config import EARLY_WARNING_LOOKBACK_HOURS


def predict_lead_time(df_current, sensor_rankings, early_detection_history=None):
    """
    Predict how far in advance anomaly will occur
    
    Args:
        df_current: Current DataFrame with sensor data (last N hours)
        sensor_rankings: DataFrame with sensor rankings by early warning capability
        early_detection_history: Historical early detection patterns (optional)
        
    Returns:
        Dictionary with:
        - predicted_lead_time_hours: Hours until anomaly
        - confidence_range: Tuple (min, max) hours
        - contributing_sensors: List of sensors triggering prediction
        - confidence: Overall confidence (0-1)
    """
    if len(df_current) == 0 or sensor_rankings is None or len(sensor_rankings) == 0:
        return {
            'predicted_lead_time_hours': None,
            'confidence_range': (None, None),
            'contributing_sensors': [],
            'confidence': 0.0
        }
    
    df_current = df_current.copy()
    if 'Timestamp' in df_current.columns:
        df_current['Timestamp'] = pd.to_datetime(df_current['Timestamp'])
        df_current = df_current.sort_values('Timestamp')
    
    # Get top early warning sensors
    top_sensors = sensor_rankings.head(10)
    
    contributing_sensors = []
    lead_times = []
    confidences = []
    
    for _, sensor_row in top_sensors.iterrows():
        sensor_name = sensor_row['sensor']
        avg_lead_time = sensor_row.get('avg_lead_time_hours', 18)
        min_lead_time = sensor_row.get('min_lead_time_hours', 12)
        max_lead_time = sensor_row.get('max_lead_time_hours', 28)
        periods_detected = sensor_row.get('periods_detected', 1)
        
        # Check if sensor shows deviation
        if sensor_name in df_current.columns:
            # Calculate deviation for recent data
            recent_data = df_current[sensor_name].tail(6)  # Last 6 hours
            mean_val = df_current[sensor_name].mean()
            std_val = df_current[sensor_name].std()
            
            if std_val > 0:
                z_scores = np.abs((recent_data - mean_val) / std_val)
                max_z = z_scores.max()
                
                # If significant deviation detected
                if max_z > 2.0:
                    # Confidence based on deviation magnitude and sensor reliability
                    sensor_confidence = min(1.0, (max_z - 2.0) / 3.0)  # 0-1 scale
                    reliability = min(1.0, periods_detected / 5.0)  # More periods = more reliable
                    combined_confidence = sensor_confidence * reliability
                    
                    if combined_confidence > 0.3:
                        contributing_sensors.append({
                            'sensor': sensor_name,
                            'deviation_z_score': max_z,
                            'avg_lead_time': avg_lead_time,
                            'confidence': combined_confidence
                        })
                        lead_times.append(avg_lead_time)
                        confidences.append(combined_confidence)
    
    if len(lead_times) == 0:
        return {
            'predicted_lead_time_hours': None,
            'confidence_range': (None, None),
            'contributing_sensors': [],
            'confidence': 0.0
        }
    
    # Weighted average of lead times based on confidence
    if sum(confidences) > 0:
        weighted_lead_time = np.average(lead_times, weights=confidences)
        overall_confidence = np.mean(confidences)
    else:
        weighted_lead_time = np.mean(lead_times)
        overall_confidence = 0.5
    
    # Calculate confidence range (min and max from contributing sensors)
    min_lead = min(lead_times) if lead_times else weighted_lead_time * 0.7
    max_lead = max(lead_times) if lead_times else weighted_lead_time * 1.3
    
    # Adjust range based on confidence
    range_size = (max_lead - min_lead) * (1 - overall_confidence)
    confidence_range = (
        max(0, weighted_lead_time - range_size),
        weighted_lead_time + range_size
    )
    
    return {
        'predicted_lead_time_hours': weighted_lead_time,
        'confidence_range': confidence_range,
        'contributing_sensors': contributing_sensors,
        'confidence': overall_confidence
    }

