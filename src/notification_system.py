"""
Notification system for two-tier anomaly alerts
Implements early warning (immediate) and priority escalation (3+ hours persistence)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from src.config import (
    NOTIFICATION_ESCALATION_HOURS,
    NOTIFICATION_ENABLED,
    NOTIFICATION_LOG_FILE,
    NOTIFICATION_DETAIL_LEVEL,
    NOTIFICATION_REALTIME
)


class NotificationManager:
    """
    Manages two-tier notification system:
    - Early Warning: Immediate notification when anomaly is first detected
    - Priority Escalation: Notification if anomaly persists 3+ hours
    """
    
    def __init__(self, detail_level=None, log_file=None, realtime=None):
        """
        Initialize NotificationManager
        
        Args:
            detail_level: 'minimal' or 'detailed' (defaults to config)
            log_file: Path to log file (defaults to config)
            realtime: Whether to send real-time notifications (defaults to config)
        """
        self.detail_level = detail_level if detail_level else NOTIFICATION_DETAIL_LEVEL
        self.log_file = log_file if log_file else NOTIFICATION_LOG_FILE
        self.realtime = realtime if realtime is not None else NOTIFICATION_REALTIME
        self.enabled = NOTIFICATION_ENABLED
        
        # Track anomaly states per asset: {asset: {anomaly_start_time, is_escalated, last_notification_time, period_id}}
        self.anomaly_states = {}
        
        # Store all notifications for batch summary
        self.notifications = []
        
        # Initialize log file
        if self.enabled and self.log_file:
            log_path = Path(self.log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(log_path, 'w') as f:
                f.write(f"=== Notification Log Started: {datetime.now()} ===\n\n")
    
    def _log_notification(self, message, level="INFO"):
        """
        Log notification to console and file
        
        Args:
            message: Message to log
            level: Log level (INFO, WARNING, ERROR)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        
        # Console logging
        print(log_message)
        
        # File logging
        if self.enabled and self.log_file:
            try:
                with open(self.log_file, 'a') as f:
                    f.write(log_message + "\n")
            except Exception as e:
                print(f"Warning: Could not write to log file: {e}")
    
    def _format_notification(self, asset, timestamp, notification_type, details):
        """
        Format notification message based on detail level
        
        Args:
            asset: Asset name
            timestamp: Timestamp of anomaly
            notification_type: 'EARLY_WARNING' or 'PRIORITY_ESCALATION'
            details: Dictionary with additional details
            
        Returns:
            Formatted notification message
        """
        if notification_type == 'EARLY_WARNING':
            base_msg = f"⚠️  EARLY WARNING - {asset}: Anomaly detected at {timestamp}"
        else:  # PRIORITY_ESCALATION
            duration = details.get('duration_hours', 0)
            base_msg = f"🚨 PRIORITY ESCALATION - {asset}: Anomaly has persisted for {duration:.1f} hours (since {details.get('start_time', 'unknown')})"
        
        if self.detail_level == 'detailed':
            # Add detailed information
            details_str = f"\n  Timestamp: {timestamp}"
            if 'anomaly_score' in details:
                details_str += f"\n  Anomaly Score: {details['anomaly_score']:.3f}"
            if 'sensor_values' in details:
                details_str += f"\n  Key Sensor Values: {details['sensor_values']}"
            if 'duration_hours' in details:
                details_str += f"\n  Duration: {details['duration_hours']:.1f} hours"
            return base_msg + details_str
        else:
            return base_msg
    
    def send_early_warning(self, asset, timestamp, details=None, realtime=None):
        """
        Send early warning notification when anomaly is first detected
        
        Args:
            asset: Asset name
            timestamp: Timestamp when anomaly was detected
            details: Optional dictionary with additional details
            realtime: Override realtime setting for this notification
        """
        if not self.enabled:
            return
        
        realtime = realtime if realtime is not None else self.realtime
        details = details or {}
        
        message = self._format_notification(asset, timestamp, 'EARLY_WARNING', details)
        
        if realtime:
            self._log_notification(message, "WARNING")
        
        # Store for batch summary
        self.notifications.append({
            'timestamp': timestamp,
            'asset': asset,
            'type': 'EARLY_WARNING',
            'message': message,
            'details': details
        })
    
    def send_priority_escalation(self, asset, timestamp, duration_hours, details=None, realtime=None):
        """
        Send priority escalation notification for persistent anomalies (3+ hours)
        
        Args:
            asset: Asset name
            timestamp: Current timestamp
            duration_hours: Duration anomaly has persisted (hours)
            details: Optional dictionary with additional details
            realtime: Override realtime setting for this notification
        """
        if not self.enabled:
            return
        
        realtime = realtime if realtime is not None else self.realtime
        details = details or {}
        details['duration_hours'] = duration_hours
        
        message = self._format_notification(asset, timestamp, 'PRIORITY_ESCALATION', details)
        
        if realtime:
            self._log_notification(message, "ERROR")
        
        # Store for batch summary
        self.notifications.append({
            'timestamp': timestamp,
            'asset': asset,
            'type': 'PRIORITY_ESCALATION',
            'message': message,
            'details': details
        })
    
    def process_anomaly_detection(self, df, asset_name, anomaly_col='anomaly_combined', realtime=None):
        """
        Process anomaly detection results and send notifications
        
        Args:
            df: DataFrame with anomaly detection results (must have 'Timestamp' and anomaly_col)
            asset_name: Name of the asset
            anomaly_col: Column name for anomaly flag
            realtime: Override realtime setting
        """
        if not self.enabled:
            return
        
        if anomaly_col not in df.columns:
            self._log_notification(f"No anomaly column '{anomaly_col}' found for {asset_name}", "WARNING")
            return
        
        if 'Timestamp' not in df.columns:
            self._log_notification(f"No 'Timestamp' column found for {asset_name}", "WARNING")
            return
        
        realtime = realtime if realtime is not None else self.realtime
        
        # Initialize asset state if not exists
        if asset_name not in self.anomaly_states:
            self.anomaly_states[asset_name] = {
                'active_periods': {},  # {period_id: {start_time, start_idx, is_escalated}}
                'next_period_id': 1
            }
        
        asset_state = self.anomaly_states[asset_name]
        
        # Sort by timestamp to ensure chronological processing
        df_sorted = df.sort_values('Timestamp').reset_index(drop=True)
        
        # Track current period
        current_period_id = None
        in_anomaly = False
        
        for idx, row in df_sorted.iterrows():
            timestamp = row['Timestamp']
            is_anomaly = bool(row[anomaly_col])
            
            if is_anomaly:
                if not in_anomaly:
                    # New anomaly period starting
                    in_anomaly = True
                    current_period_id = asset_state['next_period_id']
                    asset_state['next_period_id'] += 1
                    
                    asset_state['active_periods'][current_period_id] = {
                        'start_time': timestamp,
                        'start_idx': idx,
                        'is_escalated': False
                    }
                    
                    # Send early warning
                    details = {}
                    if self.detail_level == 'detailed':
                        # Add detailed information
                        if 'anomaly_score_combined' in df_sorted.columns:
                            details['anomaly_score'] = row.get('anomaly_score_combined', 0)
                        # Add key sensor values if available
                        sensor_cols = [col for col in df_sorted.columns if 'Speed' in col or 'Pressure' in col or 'Flow' in col]
                        if sensor_cols:
                            sensor_values = {col: row[col] for col in sensor_cols[:3] if pd.notna(row.get(col))}
                            if sensor_values:
                                details['sensor_values'] = sensor_values
                    
                    self.send_early_warning(asset_name, timestamp, details, realtime)
                
                # Check if this period needs escalation
                period_info = asset_state['active_periods'][current_period_id]
                if not period_info['is_escalated']:
                    # Calculate duration
                    duration = (timestamp - period_info['start_time']).total_seconds() / 3600  # hours
                    
                    if duration >= NOTIFICATION_ESCALATION_HOURS:
                        # Send priority escalation
                        period_info['is_escalated'] = True
                        
                        details = {'start_time': period_info['start_time'], 'duration_hours': duration}
                        if self.detail_level == 'detailed':
                            if 'anomaly_score_combined' in df_sorted.columns:
                                details['anomaly_score'] = row.get('anomaly_score_combined', 0)
                            sensor_cols = [col for col in df_sorted.columns if 'Speed' in col or 'Pressure' in col or 'Flow' in col]
                            if sensor_cols:
                                sensor_values = {col: row[col] for col in sensor_cols[:3] if pd.notna(row.get(col))}
                                if sensor_values:
                                    details['sensor_values'] = sensor_values
                        
                        self.send_priority_escalation(asset_name, timestamp, duration, details, realtime)
            else:
                if in_anomaly:
                    # Anomaly period ended
                    in_anomaly = False
                    # Keep period info for reference but mark as ended
                    if current_period_id:
                        asset_state['active_periods'][current_period_id]['end_time'] = timestamp
                    current_period_id = None
        
        # Clean up old periods (keep last 10 for reference)
        if len(asset_state['active_periods']) > 10:
            # Remove oldest periods
            sorted_periods = sorted(asset_state['active_periods'].items(), 
                                  key=lambda x: x[1].get('start_time', pd.Timestamp.min))
            periods_to_remove = sorted_periods[:-10]
            for period_id, _ in periods_to_remove:
                del asset_state['active_periods'][period_id]
    
    def generate_batch_summary(self):
        """
        Generate summary of all notifications after batch processing
        
        Returns:
            String summary of notifications
        """
        if not self.enabled or len(self.notifications) == 0:
            return "No notifications generated."
        
        summary_lines = []
        summary_lines.append("\n" + "="*60)
        summary_lines.append("NOTIFICATION SUMMARY")
        summary_lines.append("="*60)
        
        # Count by type
        early_warnings = [n for n in self.notifications if n['type'] == 'EARLY_WARNING']
        escalations = [n for n in self.notifications if n['type'] == 'PRIORITY_ESCALATION']
        
        summary_lines.append(f"\nTotal Notifications: {len(self.notifications)}")
        summary_lines.append(f"  - Early Warnings: {len(early_warnings)}")
        summary_lines.append(f"  - Priority Escalations: {len(escalations)}")
        
        # Group by asset
        by_asset = {}
        for notif in self.notifications:
            asset = notif['asset']
            if asset not in by_asset:
                by_asset[asset] = {'early_warnings': 0, 'escalations': 0}
            if notif['type'] == 'EARLY_WARNING':
                by_asset[asset]['early_warnings'] += 1
            else:
                by_asset[asset]['escalations'] += 1
        
        summary_lines.append("\nBy Asset:")
        for asset, counts in by_asset.items():
            summary_lines.append(f"  {asset}:")
            summary_lines.append(f"    - Early Warnings: {counts['early_warnings']}")
            summary_lines.append(f"    - Priority Escalations: {counts['escalations']}")
        
        # List all notifications if detail level is detailed
        if self.detail_level == 'detailed' and len(self.notifications) <= 50:
            summary_lines.append("\nAll Notifications:")
            for notif in self.notifications:
                summary_lines.append(f"  [{notif['timestamp']}] {notif['message']}")
        
        summary_lines.append("="*60 + "\n")
        
        summary = "\n".join(summary_lines)
        
        # Log summary
        if self.enabled:
            self._log_notification("Batch processing complete. Summary generated.", "INFO")
            if self.log_file:
                with open(self.log_file, 'a') as f:
                    f.write(summary + "\n")
        
        return summary
    
    def reset(self):
        """Reset notification manager state"""
        self.anomaly_states = {}
        self.notifications = []

