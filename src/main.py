"""
Main pipeline for anomaly detection system
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Import modules (all in same src/ directory)
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

def combine_anomaly_flags(df):
    """
    Combine statistical and ML anomaly flags
    
    Args:
        df: DataFrame with anomaly flags
        
    Returns:
        DataFrame with combined anomaly flag
    """
    df = df.copy()
    
    # Combine flags (OR logic: flag if either method detects anomaly)
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


def process_asset(df, asset_name, output_dir, notification_manager=None):
    """
    Process a single asset through the complete pipeline
    
    Args:
        df: DataFrame with sensor data
        asset_name: Name of asset ('Asset 1' or 'Asset 2')
        output_dir: Directory to save outputs
        notification_manager: Optional NotificationManager instance
        
    Returns:
        Tuple of (processed_df, early_detection_results)
    """
    print(f"\n{'='*60}")
    print(f"Processing {asset_name}")
    print(f"{'='*60}")
    
    # Feature engineering
    df = engineer_features(df, asset=asset_name)
    
    # Statistical detection
    df = detect_anomalies_statistical(df, asset=asset_name)
    
    # ML detection
    df = detect_anomalies_ml(df, asset=asset_name)
    
    # Combine flags
    df = combine_anomaly_flags(df)
    
    # Process notifications
    if notification_manager:
        print(f"\n=== Processing Notifications for {asset_name} ===")
        notification_manager.process_anomaly_detection(df, asset_name)
    
    # Early detection analysis
    early_detection = analyze_early_detection(df, asset=asset_name)
    
    # Create output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Visualizations
    print(f"\n=== Generating Visualizations for {asset_name} ===")
    
    # Key sensors to plot
    if asset_name == 'Asset 1':
        key_sensors = [
            'Asset 1 HP - Disch Press Value',
            'Asset 1 HP - Pressure & Ratio Value',
            'Asset 1T - Speed Value',
            'residual'
        ]
    else:
        key_sensors = [
            'Asset 2 - Disch Press Value',
            'Asset 2 Pressure & Ratio Value',
            'Asset 2T - Speed Value'
        ]
    
    # Only plot sensors that exist
    key_sensors = [s for s in key_sensors if s in df.columns]
    
    # Time series plot
    plot_time_series_with_anomalies(
        df, key_sensors[:3],  # Plot first 3 sensors
        anomaly_col='anomaly_combined',
        title=f'{asset_name} - Time Series with Anomalies',
        save_path=output_dir / f'{asset_name.replace(" ", "_")}_time_series.png'
    )
    
    # Anomaly scores plot
    plot_anomaly_scores(
        df,
        title=f'{asset_name} - Anomaly Scores',
        save_path=output_dir / f'{asset_name.replace(" ", "_")}_scores.png'
    )
    
    # Export results
    export_results(
        df,
        output_dir / f'{asset_name.replace(" ", "_")}_results.csv',
        asset=asset_name
    )
    
    return df, early_detection


def main():
    """
    Main execution function
    """
    print("="*60)
    print("Methanex Anomaly Detection System")
    print("="*60)
    
    # Configuration
    data_file = "Updated Challenge3 Data.csv"
    output_dir = "output"
    
    # Initialize notification manager
    notification_manager = NotificationManager()
    
    # Step 1: Data exploration and preparation
    print("\n" + "="*60)
    print("STEP 1: Data Exploration and Preparation")
    print("="*60)
    
    df_asset1, df_asset2, quality_metrics = prepare_data(data_file)
    
    # Step 2: Process Asset 1
    print("\n" + "="*60)
    print("STEP 2: Processing Asset 1")
    print("="*60)
    
    df_asset1_processed, early_detection_asset1 = process_asset(
        df_asset1, 'Asset 1', output_dir, notification_manager
    )
    
    # Step 3: Process Asset 2
    print("\n" + "="*60)
    print("STEP 3: Processing Asset 2")
    print("="*60)
    
    df_asset2_processed, early_detection_asset2 = process_asset(
        df_asset2, 'Asset 2', output_dir, notification_manager
    )
    
    # Step 4: Generate notification summary
    if notification_manager.enabled:
        print("\n" + "="*60)
        print("STEP 4: Notification Summary")
        print("="*60)
        notification_summary = notification_manager.generate_batch_summary()
        print(notification_summary)
    
    # Step 5: Generate summary report
    print("\n" + "="*60)
    print("STEP 5: Generating Summary Report")
    print("="*60)
    
    summary_stats = generate_summary_statistics(
        df_asset1_processed, df_asset2_processed,
        early_detection_asset1, early_detection_asset2
    )
    
    create_summary_report(
        summary_stats,
        early_detection_asset1,
        early_detection_asset2,
        output_path=Path(output_dir) / "anomaly_detection_report.md"
    )
    
    # Print summary
    print("\n" + "="*60)
    print("EXECUTION COMPLETE")
    print("="*60)
    print(f"\nResults saved to: {output_dir}/")
    print("\nSummary:")
    for asset_name, stats in summary_stats.items():
        print(f"\n{asset_name}:")
        print(f"  Total records: {stats.get('total_records', 'N/A')}")
        anomalies = stats.get('anomalies_detected', {})
        for method, count in anomalies.items():
            print(f"  {method.capitalize()} anomalies: {count}")
        if 'anomaly_percentage' in stats:
            print(f"  Anomaly percentage: {stats['anomaly_percentage']:.2f}%")
    
    return df_asset1_processed, df_asset2_processed, summary_stats


if __name__ == "__main__":
    df1, df2, summary = main()

