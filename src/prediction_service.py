"""
Prediction Service - Predicts when anomalies will occur
Combines early detection indicators with forecasting models
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.config import EARLY_WARNING_LOOKBACK_HOURS


def predict_anomaly_timing(df_current, trained_models, historical_patterns=None, sensor_rankings=None):
    """
    Predict when anomaly will occur based on current sensor patterns
    
    Args:
        df_current: Current DataFrame with sensor data (last N hours)
        trained_models: ModelManager instance with loaded models
        historical_patterns: Historical early detection patterns (optional)
        sensor_rankings: Sensor rankings from early detection (optional)
        
    Returns:
        Dictionary with:
        - predicted_timestamp: When anomaly is expected (datetime)
        - confidence: Confidence level (0-1)
        - method: Which method detected it ('early_indicator', 'forecasting', 'both')
        - lead_time_hours: Hours until predicted anomaly
        - early_indicators: List of sensors showing early warning signs
    """
    if len(df_current) == 0:
        return {
            'predicted_timestamp': None,
            'confidence': 0.0,
            'method': 'none',
            'lead_time_hours': None,
            'early_indicators': []
        }
    
    # Ensure Timestamp is datetime
    if 'Timestamp' not in df_current.columns:
        raise ValueError("DataFrame must have 'Timestamp' column")
    
    df_current = df_current.copy()
    df_current['Timestamp'] = pd.to_datetime(df_current['Timestamp'])
    df_current = df_current.sort_values('Timestamp')
    
    latest_timestamp = df_current['Timestamp'].max()
    results = {
        'predicted_timestamp': None,
        'confidence': 0.0,
        'method': 'none',
        'lead_time_hours': None,
        'early_indicators': []
    }
    
    # Method 1: Early Detection Indicators
    early_indicator_result = _analyze_early_indicators(
        df_current, sensor_rankings, historical_patterns
    )
    
    # Method 2: Forecasting (simplified - using trend analysis)
    forecasting_result = _forecast_anomaly_timing(df_current, trained_models)
    
    # Combine results - Lower threshold for early warning detection (0.3 instead of 0.5)
    # This allows detection of early warning signs even when no current anomalies exist
    if early_indicator_result['confidence'] > 0.3 or forecasting_result['confidence'] > 0.3:
        # Use the method with higher confidence, or combine if both are confident
        if early_indicator_result['confidence'] >= forecasting_result['confidence']:
            results = early_indicator_result
            results['method'] = 'early_indicator'
        else:
            results = forecasting_result
            results['method'] = 'forecasting'
        
        # If both methods agree, increase confidence
        if (early_indicator_result['confidence'] > 0.5 and 
            forecasting_result['confidence'] > 0.5 and
            abs(early_indicator_result['lead_time_hours'] - forecasting_result['lead_time_hours']) < 6):
            results['confidence'] = min(1.0, (early_indicator_result['confidence'] + forecasting_result['confidence']) / 2)
            results['method'] = 'both'
            # Average the lead times
            results['lead_time_hours'] = (early_indicator_result['lead_time_hours'] + forecasting_result['lead_time_hours']) / 2
    
    # Calculate predicted timestamp
    if results['lead_time_hours'] is not None:
        results['predicted_timestamp'] = latest_timestamp + timedelta(hours=results['lead_time_hours'])
    
    return results


def _analyze_early_indicators(df_current, sensor_rankings, historical_patterns):
    """
    Analyze current data for early warning indicators
    """
    result = {
        'confidence': 0.0,
        'lead_time_hours': None,
        'early_indicators': []
    }
    
    if sensor_rankings is None or len(sensor_rankings) == 0:
        return result
    
    # Get top early warning sensors
    top_sensors = sensor_rankings.head(5)
    
    # Check current deviations for these sensors
    early_warning_count = 0
    total_lead_time = 0
    indicators = []
    
    for _, sensor_row in top_sensors.iterrows():
        sensor_name = sensor_row['sensor']
        avg_lead_time = sensor_row.get('avg_lead_time_hours', 18)
        
        # Check if this sensor shows deviation
        if sensor_name in df_current.columns:
            # Calculate z-score for recent data
            recent_data = df_current[sensor_name].tail(6)  # Last 6 hours
            mean_val = df_current[sensor_name].mean()
            std_val = df_current[sensor_name].std()
            
            if std_val > 0:
                z_scores = np.abs((recent_data - mean_val) / std_val)
                # Lower threshold (1.5 instead of 2.0) to catch early warning signs
                if (z_scores > 1.5).any():  # Early warning deviation
                    early_warning_count += 1
                    total_lead_time += avg_lead_time
                    max_dev = z_scores.max()
                    indicators.append({
                        'sensor': sensor_name,
                        'deviation': max_dev,
                        'avg_lead_time': avg_lead_time
                    })
    
    if early_warning_count > 0:
        # Calculate confidence based on number of indicators and deviation magnitude
        base_confidence = 0.3 + (early_warning_count * 0.15)
        # Boost confidence if deviations are strong
        max_deviation = max([ind['deviation'] for ind in indicators]) if indicators else 0
        if max_deviation > 2.5:
            base_confidence += 0.2
        result['confidence'] = min(0.9, base_confidence)
        result['lead_time_hours'] = total_lead_time / early_warning_count
        result['early_indicators'] = indicators
    
    return result


def _forecast_anomaly_timing(df_current, trained_models):
    """
    Forecast anomaly timing using trend analysis
    """
    result = {
        'confidence': 0.0,
        'lead_time_hours': None,
        'early_indicators': []
    }
    
    if len(df_current) < 12:  # Need at least 12 hours of data
        return result
    
    try:
        # Get anomaly scores for current data
        df_with_scores = trained_models.predict_on_new_data(df_current, asset_name='Asset 1')
        
        if 'anomaly_score_combined' in df_with_scores.columns:
            scores = df_with_scores['anomaly_score_combined'].values
            
            # Analyze trend - if scores are increasing
            recent_scores = scores[-6:]  # Last 6 hours
            earlier_scores = scores[-12:-6]  # Previous 6 hours
            
            if len(recent_scores) > 0 and len(earlier_scores) > 0:
                recent_avg = np.mean(recent_scores)
                earlier_avg = np.mean(earlier_scores)
                
                # If scores are increasing (even slightly) - lower threshold for early detection
                if recent_avg > earlier_avg and recent_avg > 0.2:  # Lower threshold from 0.3 to 0.2
                    # Estimate time until anomaly threshold (0.7)
                    threshold = 0.7
                    if recent_avg < threshold:
                        # Linear extrapolation
                        trend = (recent_avg - earlier_avg) / 6  # per hour
                        if trend > 0:
                            hours_to_threshold = (threshold - recent_avg) / trend
                            if 0 < hours_to_threshold < 72:  # Reasonable range
                                # Confidence based on trend strength
                                trend_strength = min(1.0, trend * 10)  # Normalize trend
                                result['confidence'] = min(0.8, 0.3 + (recent_avg * 0.5) + (trend_strength * 0.2))
                                result['lead_time_hours'] = hours_to_threshold
    except Exception as e:
        print(f"  ⚠ Forecasting error: {e}")
    
    return result

