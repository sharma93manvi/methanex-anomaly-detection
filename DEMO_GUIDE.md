# Demo Guide - Methanex Anomaly Detection System

## Demo Scenarios

This guide explains how to use the three main demo scenarios for client presentations.

### Scenario 1: Batch Process - No Anomalies

**Purpose**: Demonstrate that the system correctly identifies when there are no anomalies.

**Steps**:
1. Go to "Upload & Analyze" page
2. Select "normal_30days.csv" from the test files dropdown (or upload it)
3. Click "Process Data & Generate Predictions"
4. View Results tab

**Expected Output**:
- **Status**: "System Operating Normally" (green alert)
- **Current Anomalies Detected**: 0 (or very low, <1%)
- **Future Anomaly Prediction**: None
- **Message**: "No current anomalies detected and no future anomalies predicted"
- **Recommendations**: "System Operating Normally - Continue normal monitoring"

### Scenario 2: Batch Process - Future Anomaly Prediction

**Purpose**: Demonstrate that the system can predict anomalies that will occur in a few hours, even when no current anomalies exist.

**Steps**:
1. Go to "Upload & Analyze" page
2. Select "early_warning_30days.csv" from the test files dropdown (or upload it)
3. Click "Process Data & Generate Predictions"
4. View Results tab

**Expected Output**:
- **Status**: "Future Anomaly Predicted" (orange/yellow alert)
- **Current Anomalies**: May show some, but focus is on future prediction
- **Anomaly Timing Tab**: Shows predicted timestamp when anomaly will occur
- **Lead Time Tab**: Shows hours until predicted anomaly (e.g., 18-24 hours)
- **Recommendations Tab**: Shows proactive actions to take before anomaly occurs
- **Early Warning Indicators**: Lists sensors showing early warning signs

### Scenario 3: Real-Time Stream - Progressive Prediction

**Purpose**: Demonstrate real-time monitoring with progression from normal operation → early warnings → anomaly prediction → recommendations.

**Steps**:
1. Go to "Mock Stream" page
2. Set "Stream Speed" to "Demo (0.1s)" for fast presentation
3. Set "Hours to Stream" to 6-12 hours
4. Click "Start Stream"
5. Observe the progression

**Expected Flow**:
- **Phase 1 (0-30%)**: Normal Operation
  - Multiple sensors showing normal values
  - Status: "Normal Operation"
  - No predictions
  
- **Phase 2 (30-70%)**: Early Warning Indicators
  - Sensors start showing gradual deviations
  - Status: "Early Warning Indicators Detected"
  - Prediction confidence starts increasing
  - Lead time prediction appears
  
- **Phase 3 (70-100%)**: Anomaly Prediction Active
  - Status: "Anomaly Period"
  - "Anomaly Prediction Active" alert appears
  - Shows predicted timestamp
  - Recommendations appear automatically
  - Multiple sensors showing deviations

**Key Features to Highlight**:
- Multiple sensors monitored simultaneously (6+ sensors)
- Real-time updates as data streams
- Progressive detection (normal → warning → prediction)
- Automatic recommendations when prediction is active
- Visual progression through phases

## Test Files Available

All test files are in `test_data/` directory:

1. **normal_30days.csv** - Clean data, no anomalies (for Scenario 1)
2. **early_warning_30days.csv** - Early warning indicators leading to future anomaly (for Scenario 2)
3. **single_anomaly_30days.csv** - One anomaly period
4. **multiple_anomalies_30days.csv** - Multiple anomaly periods
5. **low_severity_30days.csv** - Low severity anomaly
6. **medium_severity_30days.csv** - Medium severity anomaly
7. **high_severity_30days.csv** - High severity anomaly
8. **critical_severity_30days.csv** - Critical severity anomaly
9. **root_cause_pressure_30days.csv** - Pressure sensor root cause
10. **root_cause_speed_30days.csv** - Speed sensor root cause
11. **mixed_scenarios_90days.csv** - Long file with mixed scenarios

## Key Demo Points

1. **Predictive Capability**: System predicts anomalies BEFORE they occur (18-28 hour lead time)
2. **Early Warning System**: Detects early warning indicators even when no current anomalies exist
3. **Multi-Sensor Monitoring**: Monitors multiple sensors simultaneously
4. **Actionable Recommendations**: Provides specific actions based on predictions
5. **Real-Time Processing**: Handles both batch and streaming data
6. **Professional UI**: Clean, Methanex-branded interface suitable for client presentations

## Troubleshooting

- **If models not loading**: Run `python train_models.py` first
- **If test files missing**: Run the batch generator to create them
- **If streaming too slow**: Use "Demo (0.1s)" speed setting
- **If no predictions**: Ensure sensor rankings are available (models must be trained)

