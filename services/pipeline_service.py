"""
Pipeline Service
Wraps the existing anomaly detection pipeline with progress tracking for Streamlit
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Import existing modules
from src.data_exploration import prepare_data
from src.feature_engineering import engineer_features
from src.statistical_detection import detect_anomalies_statistical
from src.ml_detection import detect_anomalies_ml
from src.early_detection import analyze_early_detection
from src.visualization import (
    plot_time_series_with_anomalies, plot_anomaly_scores,
    generate_summary_statistics, export_results, create_summary_report
)
from src.notification_system import NotificationManager
from src.config import OUTPUT_DIR

def combine_anomaly_flags(df):
    """Combine statistical and ML anomaly flags"""
    df = df.copy()
    
    # Combine flags (OR logic)
    if 'anomaly_statistical' in df.columns and 'anomaly_ml' in df.columns:
        df['anomaly_combined'] = df['anomaly_statistical'] | df['anomaly_ml']
    elif 'anomaly_statistical' in df.columns:
        df['anomaly_combined'] = df['anomaly_statistical']
    elif 'anomaly_ml' in df.columns:
        df['anomaly_combined'] = df['anomaly_ml']
    else:
        df['anomaly_combined'] = False
    
    # Combined score (average)
    score_cols = []
    if 'anomaly_score_statistical' in df.columns:
        score_cols.append('anomaly_score_statistical')
    if 'anomaly_score_ml' in df.columns:
        score_cols.append('anomaly_score_ml')
    
    if len(score_cols) > 0:
        df['anomaly_score_combined'] = df[score_cols].mean(axis=1)
    else:
        df['anomaly_score_combined'] = 0.0
    
    return df

def process_pipeline_with_progress(file_path, progress_callback=None):
    """
    Process the complete pipeline with progress updates
    
    Args:
        file_path: Path to CSV file
        progress_callback: Function(step, name, pct, details) for progress updates
    
    Returns:
        Dictionary with processing results
    """
    results = {
        'assets': {},
        'early_warning': {},
        'visualization_files': {},
        'output_files': {},
        'total_anomalies': 0,
        'avg_lead_time': 0,
        'detection_rate': 0,
        'assets_processed': 0
    }
    
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(exist_ok=True)
    
    # Step 1: Data Loading & Exploration (0-14%)
    if progress_callback:
        progress_callback(1, "Data Loading & Exploration", 0, "Loading CSV file...")
    
    df_asset1, df_asset2, quality_metrics = prepare_data(file_path)
    
    if progress_callback:
        progress_callback(1, "Data Loading & Exploration", 14, f"Loaded {len(df_asset1)} records per asset")
    
    # Step 2: Feature Engineering (14-28%)
    if progress_callback:
        progress_callback(2, "Feature Engineering", 14, "Computing features for Asset 1...")
    
    df_asset1_features = engineer_features(df_asset1.copy(), asset='Asset 1')
    
    if progress_callback:
        progress_callback(2, "Feature Engineering", 21, "Computing features for Asset 2...")
    
    df_asset2_features = engineer_features(df_asset2.copy(), asset='Asset 2')
    
    if progress_callback:
        progress_callback(2, "Feature Engineering", 28, f"Created {len(df_asset1_features.columns)} features")
    
    # Step 3: Statistical Detection (28-42%)
    if progress_callback:
        progress_callback(3, "Statistical Anomaly Detection", 28, "Processing Asset 1...")
    
    df_asset1_statistical = detect_anomalies_statistical(df_asset1_features.copy(), asset='Asset 1')
    
    if progress_callback:
        progress_callback(3, "Statistical Anomaly Detection", 35, "Processing Asset 2...")
    
    df_asset2_statistical = detect_anomalies_statistical(df_asset2_features.copy(), asset='Asset 2')
    
    if progress_callback:
        progress_callback(3, "Statistical Anomaly Detection", 42, "Statistical detection complete")
    
    # Step 4: ML Detection (42-56%)
    if progress_callback:
        progress_callback(4, "ML-Based Anomaly Detection", 42, "Training models for Asset 1...")
    
    df_asset1_ml = detect_anomalies_ml(df_asset1_statistical.copy(), asset='Asset 1')
    
    if progress_callback:
        progress_callback(4, "ML-Based Anomaly Detection", 49, "Training models for Asset 2...")
    
    df_asset2_ml = detect_anomalies_ml(df_asset2_statistical.copy(), asset='Asset 2')
    
    if progress_callback:
        progress_callback(4, "ML-Based Anomaly Detection", 56, "ML detection complete")
    
    # Step 5: Combine Detection (56-63%)
    if progress_callback:
        progress_callback(5, "Combining Detection Methods", 56, "Merging results...")
    
    df_asset1_combined = combine_anomaly_flags(df_asset1_ml)
    df_asset2_combined = combine_anomaly_flags(df_asset2_ml)
    
    if progress_callback:
        progress_callback(5, "Combining Detection Methods", 63, "Combined detection complete")
    
    # Step 6: Notifications (63-70%)
    if progress_callback:
        progress_callback(6, "Notification System", 63, "Processing notifications...")
    
    notification_manager = NotificationManager()
    notification_manager.process_anomaly_detection(df_asset1_combined, 'Asset 1')
    notification_manager.process_anomaly_detection(df_asset2_combined, 'Asset 2')
    
    if progress_callback:
        progress_callback(6, "Notification System", 70, "Notifications processed")
    
    # Step 7: Early Detection Analysis (70-84%)
    if progress_callback:
        progress_callback(7, "Early Detection Analysis", 70, "Analyzing Asset 1...")
    
    early_detection_asset1 = analyze_early_detection(df_asset1_combined.copy(), asset='Asset 1')
    
    if progress_callback:
        progress_callback(7, "Early Detection Analysis", 77, "Analyzing Asset 2...")
    
    early_detection_asset2 = analyze_early_detection(df_asset2_combined.copy(), asset='Asset 2')
    
    if progress_callback:
        progress_callback(7, "Early Detection Analysis", 84, "Early detection analysis complete")
    
    # Step 8: Visualization & Reporting (84-100%)
    if progress_callback:
        progress_callback(8, "Visualization & Reporting", 84, "Generating visualizations...")
    
    # Generate visualizations
    key_sensors_asset1 = [
        'Asset 1 HP - Disch Press Value',
        'Asset 1 HP - Pressure & Ratio Value',
        'Asset 1T - Speed Value'
    ]
    key_sensors_asset1 = [s for s in key_sensors_asset1 if s in df_asset1_combined.columns]
    
    plot_time_series_with_anomalies(
        df_asset1_combined, key_sensors_asset1[:3],
        anomaly_col='anomaly_combined',
        title='Asset 1 - Time Series with Anomalies',
        save_path=output_path / 'Asset_1_time_series.png'
    )
    
    plot_anomaly_scores(
        df_asset1_combined,
        title='Asset 1 - Anomaly Scores',
        save_path=output_path / 'Asset_1_scores.png'
    )
    
    key_sensors_asset2 = [
        'Asset 2 - Disch Press Value',
        'Asset 2 Pressure & Ratio Value',
        'Asset 2T - Speed Value'
    ]
    key_sensors_asset2 = [s for s in key_sensors_asset2 if s in df_asset2_combined.columns]
    
    plot_time_series_with_anomalies(
        df_asset2_combined, key_sensors_asset2[:3],
        anomaly_col='anomaly_combined',
        title='Asset 2 - Time Series with Anomalies',
        save_path=output_path / 'Asset_2_time_series.png'
    )
    
    plot_anomaly_scores(
        df_asset2_combined,
        title='Asset 2 - Anomaly Scores',
        save_path=output_path / 'Asset_2_scores.png'
    )
    
    # Export results
    export_results(df_asset1_combined, output_path / 'Asset_1_results.csv', asset='Asset 1')
    export_results(df_asset2_combined, output_path / 'Asset_2_results.csv', asset='Asset 2')
    
    # Generate summary report
    summary_stats = generate_summary_statistics(
        df_asset1_combined, df_asset2_combined,
        early_detection_asset1, early_detection_asset2
    )
    
    create_summary_report(
        summary_stats,
        early_detection_asset1,
        early_detection_asset2,
        output_path=output_path / 'anomaly_detection_report.md'
    )
    
    if progress_callback:
        progress_callback(8, "Visualization & Reporting", 100, "All outputs generated")
    
    # Compile results
    results['assets']['Asset 1'] = {
        'statistical_anomalies': int(df_asset1_combined['anomaly_statistical'].sum()) if 'anomaly_statistical' in df_asset1_combined.columns else 0,
        'ml_anomalies': int(df_asset1_combined['anomaly_ml'].sum()) if 'anomaly_ml' in df_asset1_combined.columns else 0,
        'combined_anomalies': int(df_asset1_combined['anomaly_combined'].sum()),
        'ml_threshold': float(np.percentile(df_asset1_combined['anomaly_score_ml'], 95)) if 'anomaly_score_ml' in df_asset1_combined.columns else 0,
        'avg_ml_score': float(df_asset1_combined['anomaly_score_ml'].mean()) if 'anomaly_score_ml' in df_asset1_combined.columns else 0,
        'max_ml_score': float(df_asset1_combined['anomaly_score_ml'].max()) if 'anomaly_score_ml' in df_asset1_combined.columns else 0
    }
    
    results['assets']['Asset 2'] = {
        'statistical_anomalies': int(df_asset2_combined['anomaly_statistical'].sum()) if 'anomaly_statistical' in df_asset2_combined.columns else 0,
        'ml_anomalies': int(df_asset2_combined['anomaly_ml'].sum()) if 'anomaly_ml' in df_asset2_combined.columns else 0,
        'combined_anomalies': int(df_asset2_combined['anomaly_combined'].sum()),
        'ml_threshold': float(np.percentile(df_asset2_combined['anomaly_score_ml'], 95)) if 'anomaly_score_ml' in df_asset2_combined.columns else 0,
        'avg_ml_score': float(df_asset2_combined['anomaly_score_ml'].mean()) if 'anomaly_score_ml' in df_asset2_combined.columns else 0,
        'max_ml_score': float(df_asset2_combined['anomaly_score_ml'].max()) if 'anomaly_score_ml' in df_asset2_combined.columns else 0
    }
    
    # Early warning summary
    if len(early_detection_asset1.get('sensor_rankings', [])) > 0:
        top_sensor_1 = early_detection_asset1['sensor_rankings'].iloc[0]
        lead_time_1 = top_sensor_1['avg_lead_time_hours']
    else:
        lead_time_1 = 0
    
    if len(early_detection_asset2.get('sensor_rankings', [])) > 0:
        top_sensor_2 = early_detection_asset2['sensor_rankings'].iloc[0]
        lead_time_2 = top_sensor_2['avg_lead_time_hours']
    else:
        lead_time_2 = 0
    
    results['early_warning'] = {
        'avg_lead_time': (lead_time_1 + lead_time_2) / 2 if (lead_time_1 + lead_time_2) > 0 else 0,
        'max_lead_time': max(lead_time_1, lead_time_2),
        'coverage': 100.0,  # Will be calculated from actual data
        'top_sensors': pd.concat([
            early_detection_asset1['sensor_rankings'].head(5),
            early_detection_asset2['sensor_rankings'].head(5)
        ]).to_dict('records') if len(early_detection_asset1.get('sensor_rankings', [])) > 0 else []
    }
    
    # File paths
    results['visualization_files'] = {
        'Asset 1 Time Series': str(output_path / 'Asset_1_time_series.png'),
        'Asset 1 Scores': str(output_path / 'Asset_1_scores.png'),
        'Asset 2 Time Series': str(output_path / 'Asset_2_time_series.png'),
        'Asset 2 Scores': str(output_path / 'Asset_2_scores.png')
    }
    
    results['output_files'] = {
        'Asset 1 Results CSV': str(output_path / 'Asset_1_results.csv'),
        'Asset 2 Results CSV': str(output_path / 'Asset_2_results.csv'),
        'Summary Report': str(output_path / 'anomaly_detection_report.md')
    }
    
    # Summary metrics
    results['total_anomalies'] = results['assets']['Asset 1']['combined_anomalies'] + results['assets']['Asset 2']['combined_anomalies']
    results['avg_lead_time'] = results['early_warning']['avg_lead_time']
    results['detection_rate'] = (results['total_anomalies'] / (len(df_asset1_combined) + len(df_asset2_combined))) * 100
    results['assets_processed'] = 2
    
    return results

