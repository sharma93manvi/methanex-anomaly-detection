# Early Detection of Process Excursions from Sensor Data

## Overview

This project implements a comprehensive anomaly detection system for industrial sensor data. The system combines statistical methods and machine learning approaches to identify process excursions early, enabling proactive maintenance and preventing equipment failures.

## Project Structure

### Jupyter Notebook Approach

**`Anomaly_Detection_Pipeline.ipynb`** - Main interactive notebook that:
- Provides step-by-step execution with clear descriptions
- Explains what each step does and why it matters
- Makes the entire pipeline easy to understand and follow
- Can be run interactively or converted to a script

### Modular Python Files (Best Practice for Scalability)

The system maintains modular Python files for production use:

- **`config.py`**: Centralized configuration parameters
- **`data_exploration.py`**: Data loading, validation, and quality assessment
- **`feature_engineering.py`**: Feature creation and transformation
- **`statistical_detection.py`**: Rule-based anomaly detection methods
- **`ml_detection.py`**: Machine learning-based detection (Isolation Forest, Autoencoder, LSTM)
- **`early_detection.py`**: Early warning sensor analysis
- **`visualization.py`**: Plotting and reporting functions
- **`main.py`**: Production pipeline script (can be run standalone)

## Why This Architecture?

### Best Practices for Scalability

1. **Modular Design**
   - Each module has a single responsibility
   - Easy to test individual components
   - Can be reused in other projects
   - Changes to one module don't affect others

2. **Separation of Concerns**
   - **Notebook**: Documentation and interactive exploration
   - **Modules**: Reusable, testable production code
   - **Config**: Centralized parameters for easy tuning

3. **Dual Approach**
   - **Jupyter Notebook**: Perfect for understanding, debugging, and presentations
   - **Python Modules**: Perfect for production, automation, and integration

4. **Scalability Features**
   - Vectorized operations for efficiency
   - Configurable parameters
   - Easy to add new detection methods
   - Can be converted to API or scheduled jobs

## Getting Started

### Prerequisites

```bash
pip install -r requirements.txt
```

### Running the Notebook

1. Open `Anomaly_Detection_Pipeline.ipynb` in Jupyter Lab/Notebook
2. Run cells sequentially
3. Each section has markdown explanations before code execution

### Running the Production Pipeline

```bash
python main.py
```

## Pipeline Steps

1. **Data Loading & Exploration**
   - Load CSV data
   - Assess data quality
   - Filter to operating periods

2. **Feature Engineering**
   - Compute residuals
   - Calculate rate of change
   - Generate rolling statistics
   - Add time features
   - Normalize for ML models

3. **Statistical Detection**
   - Residual-based detection
   - Rolling z-score analysis
   - Moving average envelopes
   - Percentile-based thresholds
   - Sustained anomaly requirement

4. **ML-Based Detection**
   - Isolation Forest
   - Autoencoder
   - LSTM forecasting
   - Ensemble scoring

5. **Early Detection Analysis**
   - Identify anomaly periods
   - Look back analysis (48 hours)
   - Rank sensors by early warning capability

6. **Visualization & Reporting**
   - Time series plots with anomalies
   - Anomaly score visualizations
   - CSV exports
   - Markdown summary reports

## Output Files

All outputs are saved in the `output/` directory:
- `Asset_1_results.csv` / `Asset_2_results.csv`: Processed data with anomaly flags
- `Asset_1_time_series.png` / `Asset_2_time_series.png`: Time series visualizations
- `Asset_1_scores.png` / `Asset_2_scores.png`: Anomaly score plots
- `anomaly_detection_report.md`: Comprehensive summary report

## Configuration

Edit `config.py` to adjust:
- Rolling window sizes
- Z-score thresholds
- ML model parameters
- Anomaly detection thresholds
- Early warning lookback periods

## Extending the System

### Adding a New Detection Method

1. Add function to `statistical_detection.py` or `ml_detection.py`
2. Integrate into main detection pipeline
3. Update ensemble scoring if needed
4. Add visualization if desired

### Adding New Features

1. Add function to `feature_engineering.py`
2. Call from `engineer_features()` function
3. Update documentation

## Best Practices Followed

✅ **Modular Architecture**: Separated concerns into independent modules  
✅ **Documentation**: Clear descriptions before each step  
✅ **Configuration Management**: Centralized parameters  
✅ **Code Reusability**: Functions can be used independently  
✅ **Scalability**: Efficient operations, easy to extend  
✅ **Maintainability**: Clear structure, easy to update  
✅ **Testability**: Each module can be tested independently  

## Notes

- The notebook imports and uses the modular Python files
- This approach maintains both interactivity (notebook) and production-readiness (modules)
- Changes to modules automatically reflect in the notebook
- The notebook serves as both documentation and execution environment

