"""
Visualization and reporting module
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set style
try:
    plt.style.use('seaborn-v0_8-darkgrid')
except:
    plt.style.use('seaborn-darkgrid')
sns.set_palette("husl")


def plot_time_series_with_anomalies(df, columns, anomaly_col='anomaly_combined', 
                                    title='Time Series with Anomalies', 
                                    figsize=(15, 8), save_path=None):
    """
    Plot time series with anomaly periods highlighted
    
    Args:
        df: DataFrame with time series data
        columns: List of column names to plot
        anomaly_col: Name of anomaly flag column
        title: Plot title
        figsize: Figure size
        save_path: Path to save figure (optional)
    """
    if 'Timestamp' not in df.columns:
        print("Warning: Timestamp column not found")
        return
    
    n_plots = len(columns)
    fig, axes = plt.subplots(n_plots, 1, figsize=figsize, sharex=True)
    
    if n_plots == 1:
        axes = [axes]
    
    for i, col in enumerate(columns):
        if col not in df.columns:
            continue
        
        ax = axes[i]
        
        # Plot time series
        ax.plot(df['Timestamp'], df[col], label=col, linewidth=1.5, alpha=0.7)
        
        # Highlight anomaly periods
        if anomaly_col in df.columns:
            anomaly_mask = df[anomaly_col] == True
            if anomaly_mask.any():
                ax.scatter(df.loc[anomaly_mask, 'Timestamp'], 
                          df.loc[anomaly_mask, col],
                          color='red', s=20, alpha=0.6, label='Anomaly', zorder=5)
        
        ax.set_ylabel(col, fontsize=10)
        ax.legend(loc='upper right', fontsize=8)
        ax.grid(True, alpha=0.3)
    
    axes[-1].set_xlabel('Timestamp', fontsize=10)
    plt.suptitle(title, fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved plot to {save_path}")
    
    plt.close()


# Preferred order for per-model score columns (display one subplot per model)
SCORE_COLUMN_ORDER = [
    'anomaly_score_statistical',
    'anomaly_score_isolation_forest',
    'anomaly_score_autoencoder',
    'anomaly_score_lstm',
    'anomaly_score_ml',
    'anomaly_score_combined',
]
# Human-readable labels for each score column
SCORE_COLUMN_LABELS = {
    'anomaly_score_statistical': 'Statistical',
    'anomaly_score_isolation_forest': 'Isolation Forest',
    'anomaly_score_autoencoder': 'Autoencoder',
    'anomaly_score_lstm': 'LSTM',
    'anomaly_score_ml': 'ML Ensemble',
    'anomaly_score_combined': 'Combined (Stat + ML)',
}


def plot_anomaly_scores_by_model(df, title='Anomaly Scores by Model', save_path=None, figsize=(14, 4)):
    """
    Plot anomaly scores in separate subplots, one per model, so you can see
    which models detected anomalies and which did not.

    Args:
        df: DataFrame with Timestamp and anomaly_score_* columns
        title: Overall figure title
        save_path: Path to save figure (optional)
        figsize: (width, height_per_subplot) — total height = height_per_subplot * n_models
    """
    if 'Timestamp' not in df.columns:
        print("Warning: Timestamp column not found")
        return

    # Build list of score columns that exist, in preferred order
    score_cols = [c for c in SCORE_COLUMN_ORDER if c in df.columns]
    if not score_cols:
        fallback = [col for col in df.columns if 'anomaly_score' in col]
        score_cols = fallback if fallback else []

    if len(score_cols) == 0:
        print("No anomaly score columns found")
        return

    n = len(score_cols)
    height_per = figsize[1]
    fig, axes = plt.subplots(n, 1, figsize=(figsize[0], n * height_per), sharex=True)
    if n == 1:
        axes = [axes]

    for ax, col in zip(axes, score_cols):
        label = SCORE_COLUMN_LABELS.get(col, col.replace('anomaly_score_', '').replace('_', ' ').title())
        series = df[col].dropna()
        ax.plot(df['Timestamp'], df[col], color='#2e86ab', linewidth=1.2, alpha=0.9)

        # Per-model 95th percentile threshold
        if len(series) > 0:
            threshold = np.percentile(series, 95)
            ax.axhline(y=threshold, color='#e94f37', linestyle='--', linewidth=1.5,
                       label=f'Threshold (p95={threshold:.3f})')
            above = df[col] >= threshold
            if above.any():
                ax.scatter(df.loc[above, 'Timestamp'], df.loc[above, col],
                           color='#e94f37', s=12, alpha=0.7, zorder=5, label='Flagged')

        ax.set_ylabel('Score', fontsize=10)
        ax.set_title(label, fontsize=12, fontweight='bold')
        ax.legend(loc='upper right', fontsize=8)
        ax.grid(True, alpha=0.3)
        ax.set_ylim(-0.05, 1.05)

    axes[-1].set_xlabel('Timestamp', fontsize=12)
    plt.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved plot to {save_path}")

    plt.close()


def plot_anomaly_scores(df, title='Anomaly Scores Over Time', save_path=None):
    """
    Plot anomaly scores from different methods (all in one axes).

    Args:
        df: DataFrame with anomaly scores
        title: Plot title
        save_path: Path to save figure (optional)
    """
    if 'Timestamp' not in df.columns:
        print("Warning: Timestamp column not found")
        return

    score_cols = [col for col in df.columns if 'anomaly_score' in col]

    if len(score_cols) == 0:
        print("No anomaly score columns found")
        return

    fig, ax = plt.subplots(figsize=(15, 6))

    for col in score_cols:
        ax.plot(df['Timestamp'], df[col], label=col.replace('anomaly_score_', ''), 
                linewidth=1.5, alpha=0.7)

    # Add threshold line if ensemble score exists
    if 'anomaly_score_ml' in df.columns:
        threshold = np.percentile(df['anomaly_score_ml'].dropna(), 95)
        ax.axhline(y=threshold, color='red', linestyle='--', 
                  label=f'ML Threshold ({threshold:.3f})', linewidth=2)

    ax.set_xlabel('Timestamp', fontsize=12)
    ax.set_ylabel('Anomaly Score', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved plot to {save_path}")

    plt.close()


def generate_summary_statistics(df_asset1, df_asset2, early_detection_asset1, early_detection_asset2):
    """
    Generate summary statistics
    
    Args:
        df_asset1: DataFrame for Asset 1 with anomaly flags
        df_asset2: DataFrame for Asset 2 with anomaly flags
        early_detection_asset1: Early detection results for Asset 1
        early_detection_asset2: Early detection results for Asset 2
        
    Returns:
        Dictionary with summary statistics
    """
    summary = {
        'Asset 1': {},
        'Asset 2': {}
    }
    
    for asset_name, df, early_det in [('Asset 1', df_asset1, early_detection_asset1),
                                      ('Asset 2', df_asset2, early_detection_asset2)]:
        if df is None or len(df) == 0:
            continue
        
        asset_summary = {
            'total_records': len(df),
            'anomalies_detected': {}
        }
        
        # Count anomalies by method
        if 'anomaly_statistical' in df.columns:
            asset_summary['anomalies_detected']['statistical'] = int(df['anomaly_statistical'].sum())
        
        if 'anomaly_ml' in df.columns:
            asset_summary['anomalies_detected']['ml'] = int(df['anomaly_ml'].sum())
        
        if 'anomaly_combined' in df.columns:
            asset_summary['anomalies_detected']['combined'] = int(df['anomaly_combined'].sum())
            asset_summary['anomaly_percentage'] = (df['anomaly_combined'].sum() / len(df)) * 100
        
        # Holdout (30%) metrics: threshold was computed from training 70% only
        if 'is_holdout' in df.columns and 'anomaly_ml' in df.columns:
            holdout = df['is_holdout']
            n_holdout = int(holdout.sum())
            if n_holdout > 0:
                n_anom_holdout = int(df.loc[holdout, 'anomaly_ml'].sum())
                asset_summary['holdout_records'] = n_holdout
                asset_summary['holdout_anomalies_ml'] = n_anom_holdout
                asset_summary['holdout_anomaly_rate_pct'] = (n_anom_holdout / n_holdout) * 100
        
        # Early detection info
        if early_det and 'anomaly_periods' in early_det:
            asset_summary['anomaly_periods'] = len(early_det['anomaly_periods'])
            if len(early_det['sensor_rankings']) > 0:
                asset_summary['top_early_warning_sensor'] = early_det['sensor_rankings'].iloc[0]['sensor']
                asset_summary['avg_lead_time_hours'] = early_det['sensor_rankings'].iloc[0]['avg_lead_time_hours']
        
        summary[asset_name] = asset_summary
    
    return summary


def export_results(df, output_path, asset='Asset 1'):
    """
    Export results to CSV
    
    Args:
        df: DataFrame with results
        output_path: Path to save CSV
        asset: Asset name
    """
    # Select key columns for export
    export_cols = ['Timestamp']
    
    # Add sensor columns
    sensor_cols = [col for col in df.columns if any(x in col for x in 
                ['Press', 'Speed', 'flow', 'Ratio', 'residual', 'target', 'Temperature'])]
    export_cols.extend(sensor_cols)
    
    # Add anomaly flags and scores
    anomaly_cols = [col for col in df.columns if 'anomaly' in col.lower()]
    export_cols.extend(anomaly_cols)
    if 'is_holdout' in df.columns:
        export_cols.append('is_holdout')
    
    # Only include columns that exist
    export_cols = [col for col in export_cols if col in df.columns]
    
    df_export = df[export_cols].copy()
    df_export.to_csv(output_path, index=False)
    print(f"Exported results to {output_path}")


def create_summary_report(summary_stats, early_detection_asset1, early_detection_asset2, 
                         output_path='anomaly_detection_report.md'):
    """
    Create markdown summary report
    
    Args:
        summary_stats: Dictionary with summary statistics
        early_detection_asset1: Early detection results for Asset 1
        early_detection_asset2: Early detection results for Asset 2
        output_path: Path to save report
    """
    report = []
    report.append("# Anomaly Detection Report\n")
    report.append("## Summary Statistics\n\n")
    
    for asset_name, stats in summary_stats.items():
        report.append(f"### {asset_name}\n\n")
        report.append(f"- **Total Records**: {stats.get('total_records', 'N/A')}\n")
        
        anomalies = stats.get('anomalies_detected', {})
        if anomalies:
            report.append("- **Anomalies Detected**:\n")
            for method, count in anomalies.items():
                report.append(f"  - {method.capitalize()}: {count}\n")
        
        if 'anomaly_percentage' in stats:
            report.append(f"- **Anomaly Percentage**: {stats['anomaly_percentage']:.2f}%\n")
        
        # Holdout (30%) metrics: threshold from training 70% only
        if 'holdout_records' in stats and stats.get('holdout_records', 0) > 0:
            report.append(f"- **Holdout (last 30%)**: {stats.get('holdout_anomalies_ml', 0)} ML anomalies ({stats.get('holdout_anomaly_rate_pct', 0):.2f}% of {stats['holdout_records']} records)\n")
        
        if 'anomaly_periods' in stats:
            report.append(f"- **Anomaly Periods**: {stats['anomaly_periods']}\n")
        
        if 'top_early_warning_sensor' in stats:
            report.append(f"- **Top Early Warning Sensor**: {stats['top_early_warning_sensor']}\n")
            report.append(f"- **Average Lead Time**: {stats.get('avg_lead_time_hours', 0):.1f} hours\n")
        
        report.append("\n")
    
    # Early detection rankings
    report.append("## Early Warning Sensor Rankings\n\n")
    
    for asset_name, early_det in [('Asset 1', early_detection_asset1), 
                                  ('Asset 2', early_detection_asset2)]:
        if early_det and len(early_det.get('sensor_rankings', [])) > 0:
            report.append(f"### {asset_name}\n\n")
            rankings = early_det['sensor_rankings'].head(10)
            report.append(rankings.to_markdown(index=False))
            report.append("\n\n")
    
    # Write report
    with open(output_path, 'w') as f:
        f.write(''.join(report))
    
    print(f"Saved summary report to {output_path}")

