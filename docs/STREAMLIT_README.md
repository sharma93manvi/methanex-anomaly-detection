# Streamlit Web Application

## Quick Start

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Streamlit app:
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### Features

- **Homepage**: Navigation and overview
- **Batch Processing**: Upload CSV files and process through the complete pipeline
- **Data Stream**: Simulate real-time data streaming
- **Results Dashboard**: Comprehensive view of all analysis results

### Pages

1. **Home** (`pages/Home.py`): Welcome page with navigation cards
2. **Batch Processing** (`pages/Batch_Processing.py`): File upload and batch processing
3. **Data Stream** (`pages/Data_Stream.py`): Real-time streaming simulation
4. **Results Dashboard** (`pages/Results_Dashboard.py`): Comprehensive results view

### Services

- **Pipeline Service** (`services/pipeline_service.py`): Wraps the existing pipeline with progress tracking

### Project Structure

```
.
├── app.py                          # Main Streamlit application
├── pages/
│   ├── Home.py                     # Homepage
│   ├── Batch_Processing.py         # Batch processing page
│   ├── Data_Stream.py              # Data streaming page
│   └── Results_Dashboard.py        # Results dashboard
├── services/
│   └── pipeline_service.py         # Pipeline wrapper with progress
└── requirements.txt                 # Dependencies (includes streamlit, plotly)
```

### Usage

1. **Batch Processing**:
   - Go to "Batch Processing" page
   - Upload a CSV file
   - Click "Start Processing"
   - View results in real-time with progress tracking
   - Download results when complete

2. **Data Stream**:
   - Go to "Data Stream" page
   - Select or upload a data file
   - Configure chunk size and delay
   - Click "Start Streaming"
   - Watch real-time processing

3. **Results Dashboard**:
   - After processing, go to "Results Dashboard"
   - View comprehensive analysis
   - Explore interactive visualizations
   - Review sensor rankings and early warning metrics

### Deployment

For GCP deployment:

```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

Then access via `http://<VM_IP>:8501`

