"""
Root Cause Analyzer - Identifies root cause of anomalies
Combines feature importance, sensor ranking, and correlation analysis
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest


def analyze_root_cause(df_current, trained_models, sensor_rankings=None):
    """
    Identify root cause of anomaly
    
    Args:
        df_current: Current DataFrame with sensor data and anomaly flags
        trained_models: ModelManager instance with loaded models
        sensor_rankings: Sensor rankings from early detection (optional)
        
    Returns:
        Dictionary with:
        - primary_cause: Top sensor/feature causing anomaly
        - contributing_factors: List of contributing sensors
        - confidence: Confidence in root cause identification (0-1)
        - evidence: Supporting evidence from each method
    """
    result = {
        'primary_cause': None,
        'contributing_factors': [],
        'confidence': 0.0,
        'evidence': {
            'feature_importance': {},
            'sensor_ranking': {},
            'statistical_correlation': {}
        }
    }
    
    if len(df_current) == 0:
        return result
    
    df_current = df_current.copy()
    
    # Method 1: Feature Importance (from Isolation Forest)
    feature_importance_result = _analyze_feature_importance(df_current, trained_models)
    result['evidence']['feature_importance'] = feature_importance_result
    
    # Method 2: Sensor Ranking (from early detection)
    sensor_ranking_result = _analyze_sensor_ranking(df_current, sensor_rankings)
    result['evidence']['sensor_ranking'] = sensor_ranking_result
    
    # Method 3: Statistical Correlation
    correlation_result = _analyze_statistical_correlation(df_current)
    result['evidence']['statistical_correlation'] = correlation_result
    
    # Combine results
    all_causes = {}
    
    # Weight feature importance results
    if feature_importance_result.get('top_features'):
        for feature, importance in feature_importance_result['top_features'].items():
            if feature not in all_causes:
                all_causes[feature] = {'score': 0, 'methods': []}
            all_causes[feature]['score'] += importance * 0.4  # 40% weight
            all_causes[feature]['methods'].append('feature_importance')
    
    # Weight sensor ranking results
    if sensor_ranking_result.get('top_sensors'):
        for sensor, score in sensor_ranking_result['top_sensors'].items():
            if sensor not in all_causes:
                all_causes[sensor] = {'score': 0, 'methods': []}
            all_causes[sensor]['score'] += score * 0.3  # 30% weight
            all_causes[sensor]['methods'].append('sensor_ranking')
    
    # Weight correlation results
    if correlation_result.get('top_sensors'):
        for sensor, correlation in correlation_result['top_sensors'].items():
            if sensor not in all_causes:
                all_causes[sensor] = {'score': 0, 'methods': []}
            all_causes[sensor]['score'] += abs(correlation) * 0.3  # 30% weight
            all_causes[sensor]['methods'].append('statistical_correlation')
    
    # Sort by combined score
    if all_causes:
        sorted_causes = sorted(all_causes.items(), key=lambda x: x[1]['score'], reverse=True)
        
        # Primary cause
        primary_cause_name = sorted_causes[0][0]
        primary_cause_data = sorted_causes[0][1]
        
        result['primary_cause'] = {
            'sensor': primary_cause_name,
            'score': primary_cause_data['score'],
            'methods': primary_cause_data['methods']
        }
        
        # Contributing factors (top 5)
        result['contributing_factors'] = [
            {
                'sensor': name,
                'score': data['score'],
                'methods': data['methods']
            }
            for name, data in sorted_causes[1:6]
        ]
        
        # Confidence based on agreement between methods
        num_methods_agreeing = len(primary_cause_data['methods'])
        result['confidence'] = min(1.0, 0.5 + (num_methods_agreeing * 0.15))
    
    return result


def _analyze_feature_importance(df_current, trained_models):
    """
    Analyze feature importance from Isolation Forest
    """
    result = {'top_features': {}}
    
    try:
        # Get feature importances if available
        asset_name = 'Asset 1'  # Default, could be parameterized
        if asset_name in trained_models.models:
            iso_forest = trained_models.models[asset_name].get('isolation_forest')
            
            if iso_forest and hasattr(iso_forest, 'feature_importances_'):
                feature_cols = trained_models.feature_cols.get(asset_name, [])
                
                if len(feature_cols) > 0:
                    importances = iso_forest.feature_importances_
                    
                    # Get top 10 features
                    top_indices = np.argsort(importances)[-10:][::-1]
                    
                    for idx in top_indices:
                        if idx < len(feature_cols):
                            feature_name = feature_cols[idx]
                            result['top_features'][feature_name] = float(importances[idx])
    except Exception as e:
        print(f"  ⚠ Feature importance analysis error: {e}")
    
    return result


def _analyze_sensor_ranking(df_current, sensor_rankings):
    """
    Analyze based on sensor rankings from early detection
    """
    result = {'top_sensors': {}}
    
    if sensor_rankings is None or len(sensor_rankings) == 0:
        return result
    
    # Get top sensors and check their current values
    top_sensors = sensor_rankings.head(10)
    
    for _, sensor_row in top_sensors.iterrows():
        sensor_name = sensor_row['sensor']
        
        if sensor_name in df_current.columns:
            # Calculate deviation
            recent_data = df_current[sensor_name].tail(6)
            mean_val = df_current[sensor_name].mean()
            std_val = df_current[sensor_name].std()
            
            if std_val > 0:
                z_score = abs((recent_data - mean_val) / std_val).max()
                
                # Score based on deviation and sensor ranking
                ranking_score = 1.0 / (sensor_row.name + 1)  # Higher rank = higher score
                deviation_score = min(1.0, z_score / 3.0)
                
                result['top_sensors'][sensor_name] = ranking_score * deviation_score
    
    return result


def _analyze_statistical_correlation(df_current):
    """
    Analyze statistical correlation between sensors and anomaly flags
    """
    result = {'top_sensors': {}}
    
    if 'anomaly_combined' not in df_current.columns and 'anomaly_score_combined' not in df_current.columns:
        return result
    
    # Use anomaly score if available, otherwise use flag
    if 'anomaly_score_combined' in df_current.columns:
        anomaly_col = 'anomaly_score_combined'
    else:
        anomaly_col = 'anomaly_combined'
        df_current = df_current.copy()
        df_current[anomaly_col] = df_current[anomaly_col].astype(float)
    
    # Get sensor columns
    sensor_cols = [col for col in df_current.columns 
                   if ('Asset' in col and 'Value' in col) or 
                      ('Pressure' in col or 'Speed' in col or 'flow' in col)]
    
    for col in sensor_cols:
        if col in df_current.columns:
            try:
                # Calculate correlation
                correlation = df_current[col].corr(df_current[anomaly_col])
                
                if pd.notna(correlation) and abs(correlation) > 0.3:
                    result['top_sensors'][col] = float(correlation)
            except Exception:
                continue
    
    return result

