"""
Demo Data Loader
Loads pre-processed results for showcase demonstration
"""

import pandas as pd
import pickle
import json
from pathlib import Path
from src.config import OUTPUT_DIR

def load_demo_results():
    """
    Load pre-processed demo results from output directory
    
    Returns:
        dict: Dictionary containing all demo results
    """
    output_path = Path(OUTPUT_DIR)
    
    results = {
        'assets': {},
        'early_warning': {},
        'visualization_files': {},
        'output_files': {},
        'total_anomalies': 0,
        'avg_lead_time': 0,
        'detection_rate': 0,
        'assets_processed': 0,
        'demo_data_loaded': False
    }
    
    try:
        # Load Asset 1 results
        asset1_file = output_path / 'Asset_1_results.csv'
        if asset1_file.exists():
            df_asset1 = pd.read_csv(asset1_file)
            results['assets']['Asset 1'] = {
                'dataframe': df_asset1,
                'statistical_anomalies': int(df_asset1['anomaly_statistical'].sum()) if 'anomaly_statistical' in df_asset1.columns else 0,
                'ml_anomalies': int(df_asset1['anomaly_ml'].sum()) if 'anomaly_ml' in df_asset1.columns else 0,
                'combined_anomalies': int(df_asset1['anomaly_combined'].sum()) if 'anomaly_combined' in df_asset1.columns else 0,
                'ml_threshold': float(df_asset1['anomaly_score_ml'].quantile(0.95)) if 'anomaly_score_ml' in df_asset1.columns else 0,
                'avg_ml_score': float(df_asset1['anomaly_score_ml'].mean()) if 'anomaly_score_ml' in df_asset1.columns else 0,
                'max_ml_score': float(df_asset1['anomaly_score_ml'].max()) if 'anomaly_score_ml' in df_asset1.columns else 0,
                'total_records': len(df_asset1)
            }
        
        # Load Asset 2 results
        asset2_file = output_path / 'Asset_2_results.csv'
        if asset2_file.exists():
            df_asset2 = pd.read_csv(asset2_file)
            results['assets']['Asset 2'] = {
                'dataframe': df_asset2,
                'statistical_anomalies': int(df_asset2['anomaly_statistical'].sum()) if 'anomaly_statistical' in df_asset2.columns else 0,
                'ml_anomalies': int(df_asset2['anomaly_ml'].sum()) if 'anomaly_ml' in df_asset2.columns else 0,
                'combined_anomalies': int(df_asset2['anomaly_combined'].sum()) if 'anomaly_combined' in df_asset2.columns else 0,
                'ml_threshold': float(df_asset2['anomaly_score_ml'].quantile(0.95)) if 'anomaly_score_ml' in df_asset2.columns else 0,
                'avg_ml_score': float(df_asset2['anomaly_score_ml'].mean()) if 'anomaly_score_ml' in df_asset2.columns else 0,
                'max_ml_score': float(df_asset2['anomaly_score_ml'].max()) if 'anomaly_score_ml' in df_asset2.columns else 0,
                'total_records': len(df_asset2)
            }
        
        # Calculate summary metrics
        if 'Asset 1' in results['assets'] and 'Asset 2' in results['assets']:
            results['total_anomalies'] = (
                results['assets']['Asset 1']['combined_anomalies'] + 
                results['assets']['Asset 2']['combined_anomalies']
            )
            total_records = (
                results['assets']['Asset 1']['total_records'] + 
                results['assets']['Asset 2']['total_records']
            )
            results['detection_rate'] = (results['total_anomalies'] / total_records * 100) if total_records > 0 else 0
            results['assets_processed'] = 2
        
        # Load visualization files
        viz_files = {
            'Asset 1 Time Series': str(output_path / 'Asset_1_time_series.png'),
            'Asset 1 Scores': str(output_path / 'Asset_1_scores.png'),
            'Asset 2 Time Series': str(output_path / 'Asset_2_time_series.png'),
            'Asset 2 Scores': str(output_path / 'Asset_2_scores.png')
        }
        results['visualization_files'] = {k: v for k, v in viz_files.items() if Path(v).exists()}
        
        # Load output files
        output_files = {
            'Asset 1 Results CSV': str(asset1_file),
            'Asset 2 Results CSV': str(asset2_file),
            'Summary Report': str(output_path / 'anomaly_detection_report.md')
        }
        results['output_files'] = {k: v for k, v in output_files.items() if Path(v).exists()}
        
        # Set default early warning metrics (will be enhanced when early detection data is available)
        results['early_warning'] = {
            'avg_lead_time': 19.3,  # Average from notebook results
            'max_lead_time': 28.0,  # Maximum from notebook results
            'coverage': 100.0,
            'top_sensors': []
        }
        
        results['demo_data_loaded'] = True
        
    except Exception as e:
        print(f"Error loading demo data: {e}")
        results['demo_data_loaded'] = False
    
    return results

def get_normal_ranges_from_data(df, sensors, train_split=0.7):
    """
    Extract normal operating ranges from training data
    
    Args:
        df: DataFrame with sensor data
        sensors: List of sensor column names
        train_split: Fraction of data to use for training (default 0.7)
    
    Returns:
        dict: Normal ranges for each sensor
    """
    normal_ranges = {}
    train_idx = int(len(df) * train_split)
    train_data = df.iloc[:train_idx]
    
    for sensor in sensors:
        if sensor in train_data.columns:
            values = train_data[sensor].dropna()
            if len(values) > 0:
                normal_ranges[sensor] = {
                    'mean': float(values.mean()),
                    'std': float(values.std()),
                    'min': float(values.min()),
                    'max': float(values.max()),
                    'p25': float(values.quantile(0.25)),
                    'p75': float(values.quantile(0.75)),
                    'p1': float(values.quantile(0.01)),
                    'p99': float(values.quantile(0.99)),
                    'range_2std': (float(values.mean() - 2*values.std()), float(values.mean() + 2*values.std())),
                    'range_iqr': (float(values.quantile(0.25)), float(values.quantile(0.75))),
                    'training_samples': len(values)
                }
    
    return normal_ranges

