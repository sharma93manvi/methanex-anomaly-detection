"""
Configuration parameters for anomaly detection system
"""

# Rolling window sizes (in hours, since data is hourly)
ROLLING_WINDOW_SHORT = 6   # 6 hours - Recent patterns, quick changes
ROLLING_WINDOW_LONG = 24   # 24 hours - Daily patterns, long term trends

# Z-score threshold for statistical detection
Z_SCORE_THRESHOLD = 3.0 # Flags values >3 standard deviations from the mean

# Percentile thresholds for statistical detection
PERCENTILE_LOW = 1   # 1st percentile
PERCENTILE_HIGH = 99  # 99th percentile

# Sustained anomaly duration (hours) - Requires anomalies to persist for 3+ hours before flagging
SUSTAINED_ANOMALY_DURATION = 3 # Aligns with notification escalation threshold (3 hours)

# Operating period thresholds - Asset is operating if Speed > 1000 OR Steam Flow > 0
ASSET1_SPEED_THRESHOLD = 1000
ASSET1_FLOW_THRESHOLD = 0
ASSET2_SPEED_THRESHOLD = 1000
ASSET2_FLOW_THRESHOLD = 0

# ML model parameters
TRAIN_SPLIT = 0.7  # Use first 70% of data for training

## Isolation Forest Parameters
ISOLATION_FOREST_CONTAMINATION = 0.05  # Expect 5% anomalies in training data(typically between 1%-10%), Higher = more sensitive (flags more as anomalies) 

## Autoencoder Parameters
AUTOENCODER_EPOCHS = 50 # Number of full passes through training data
AUTOENCODER_BATCH_SIZE = 32 # Number of samples processed before updating weights

## LSTM Parameters - typically needs fewer epochs for time series
LSTM_EPOCHS = 30 
LSTM_BATCH_SIZE = 32  

# Anomaly score threshold (percentile) - After combining all ML methods, ranks scores and flags the highest 5%
ANOMALY_SCORE_PERCENTILE = 95  # Top 5% flagged as anomalies

# Early detection parameters
EARLY_WARNING_LOOKBACK_HOURS = 48  # Look back 48 hours before anomaly

# Notification system parameters
NOTIFICATION_ESCALATION_HOURS = 3  # Escalate if anomaly persists 3+ hours
NOTIFICATION_ENABLED = True  # Enable/disable notifications
NOTIFICATION_LOG_FILE = "notifications.log"  # Log file path
NOTIFICATION_DETAIL_LEVEL = "minimal"  # "minimal" or "detailed"
NOTIFICATION_REALTIME = True  # Send notifications in real-time during processing

# Output directory
OUTPUT_DIR = "output"  # Directory for saving results, visualizations, and reports

