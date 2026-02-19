---
name: Web Application for Anomaly Detection (Streamlit)
overview: Create a Streamlit web application for batch file processing and simulated data streaming with real-time progress tracking, interactive visualizations, and anomaly analysis results.
todos:
  - id: setup-structure
    content: Create project structure with streamlit app directory
    status: pending
  - id: streamlit-app
    content: Create main Streamlit app.py with navigation and page routing
    status: pending
    dependencies:
      - setup-structure
  - id: homepage
    content: Create homepage with two clickable cards for batch and stream options
    status: pending
    dependencies:
      - streamlit-app
  - id: pipeline-service
    content: Create pipeline_service.py to wrap existing modules with progress tracking
    status: pending
    dependencies:
      - setup-structure
  - id: stream-service
    content: Create stream_service.py for simulated data streaming with chunk processing
    status: pending
    dependencies:
      - setup-structure
  - id: batch-page
    content: Create batch processing page with file upload and progress tracker
    status: pending
    dependencies:
      - streamlit-app
      - pipeline-service
  - id: stream-page
    content: Create data streaming page with start/stop controls and live updates
    status: pending
    dependencies:
      - streamlit-app
      - stream-service
  - id: timeline-visualization
    content: Implement interactive timeline charts using Plotly in Streamlit
    status: pending
    dependencies:
      - streamlit-app
  - id: factors-display
    content: Create components to display contributing factors and sensor rankings
    status: pending
    dependencies:
      - streamlit-app
  - id: recommendations-display
    content: Create components to display actionable recommendations
    status: pending
    dependencies:
      - streamlit-app
  - id: integrate-modules
    content: Integrate existing Python modules (data_exploration, feature_engineering, etc.) into pipeline service
    status: pending
    dependencies:
      - pipeline-service
  - id: progress-tracking
    content: Implement real-time progress tracking using st.progress() and st.empty() containers
    status: pending
    dependencies:
      - pipeline-service
      - stream-service
      - batch-page
      - stream-page
  - id: test-locally
    content: Test complete flow locally: batch processing, streaming, visualizations
    status: pending
    dependencies:
      - batch-page
      - stream-page
      - timeline-visualization
      - factors-display
      - recommendations-display
  - id: deploy-gcp
    content: Deploy to GCP VM with systemd service and optional Nginx reverse proxy
    status: pending
    dependencies:
      - test-locally
---

# Web Application for Anomaly Detection System (Streamlit)

## Architecture Overview

The application will use **Streamlit**, a Python-based framework that allows direct integration with existing Python modules while providing an interactive web interface.

```
┌─────────────────────┐
│  Streamlit App      │
│  (Port 8501)        │
│                     │
│  - UI Components    │
│  - File Upload      │
│  - Progress Bars    │
│  - Plotly Charts    │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  Existing Python    │
│  Modules            │
│                     │
│  - data_exploration │
│  - feature_eng      │
│  - detection        │
│  - visualization    │
└─────────────────────┘
```

## Technology Stack

### Application Framework
- **Streamlit** - Python web framework for data apps
- **Plotly** - Interactive visualizations (same library as Plotly.js, fully interactive)
- **Pandas & NumPy** - Data processing (already in use)
- Existing Python modules: `data_exploration.py`, `feature_engineering.py`, `statistical_detection.py`, `ml_detection.py`, `early_detection.py`, `visualization.py`

### Deployment
- **GCP VM** - Single server deployment
- **systemd** or **screen/tmux** - Process management
- **Nginx** (optional) - Reverse proxy for HTTPS
- **Let's Encrypt** (optional) - SSL certificates

## Project Structure

```
anomaly-detection-app/
├── app.py                    # Main Streamlit application
├── pages/
│   ├── 1_🏠_Home.py          # Homepage
│   ├── 2_📁_Batch_Processing.py
│   └── 3_📊_Data_Stream.py
├── services/
│   ├── pipeline_service.py    # Pipeline wrapper with progress
│   └── stream_service.py      # Streaming service
├── utils/
│   ├── progress_tracker.py   # Progress tracking utilities
│   └── visualization_utils.py # Chart helpers
├── config.py                  # Configuration (existing)
├── data_exploration.py        # Existing modules
├── feature_engineering.py
├── statistical_detection.py
├── ml_detection.py
├── early_detection.py
├── visualization.py
├── requirements.txt           # Updated with streamlit, plotly
└── README.md
```

## Implementation Details

### 1. Main Application (`app.py`)

- Streamlit app initialization
- Page routing using Streamlit's multi-page app feature
- Session state management for:
  - Current job status
  - Processing results
  - Streaming state
  - Uploaded files

### 2. Homepage (`pages/1_🏠_Home.py`)

- Two large clickable cards using `st.columns()` and `st.container()`
- Navigation to batch processing or data stream pages
- Welcome message and brief description

### 3. Batch Processing Page (`pages/2_📁_Batch_Processing.py`)

**File Upload:**
- `st.file_uploader()` for CSV file selection
- File validation and preview

**Progress Tracking:**
- `st.progress()` for overall progress bar
- `st.status()` or custom containers for step-by-step updates
- Real-time updates using `st.empty()` containers
- Display:
  - Current step (1-7)
  - Step name and description
  - Progress percentage
  - Estimated time remaining

**Results Display:**
- Interactive timeline charts (Plotly)
- Anomaly factors table
- Recommendations section
- Download buttons for results

### 4. Data Stream Page (`pages/3_📊_Data_Stream.py`)

**Controls:**
- `st.button()` for Start/Stop streaming
- File selector for mock data source

**Real-time Display:**
- `st.empty()` containers for live updates
- Live anomaly counter
- Current processing chunk info
- Real-time charts updating as data streams

**Streaming Logic:**
- Read CSV in chunks
- Process each chunk
- Update UI in real-time
- Use `time.sleep()` to simulate streaming speed

### 5. Pipeline Service (`services/pipeline_service.py`)

- Wrapper around existing modules
- Progress callback integration
- Step-by-step execution with status updates:
  1. Data Loading & Validation
  2. Data Quality Assessment
  3. Feature Engineering
  4. Statistical Detection
  5. ML Detection
  6. Early Detection Analysis
  7. Visualization Generation

**Progress Callback Pattern:**
```python
def process_with_progress(file_path, progress_callback):
    progress_callback(step=1, name="Loading Data", pct=0)
    df = load_data(file_path)
    progress_callback(step=1, name="Loading Data", pct=100)
    # ... continue for each step
```

### 6. Stream Service (`services/stream_service.py`)

- Simulated data streaming (reads CSV in chunks)
- Real-time anomaly detection on streaming chunks
- Yields results for each chunk
- Configurable chunk size and delay

### 7. Visualization Components

**Timeline Charts (`utils/visualization_utils.py`):**
- Plotly interactive charts
- Features:
  - Zoom and pan (built into Plotly)
  - Hover tooltips
  - Filter by sensor (using Streamlit widgets)
  - Anomaly markers (red dots/areas)
  - Time range selection

**Example:**
```python
import plotly.graph_objects as go
import streamlit as st

fig = go.Figure()
# Add sensor data
fig.add_trace(go.Scatter(x=timestamps, y=values, name="Sensor"))
# Add anomaly markers
fig.add_trace(go.Scatter(x=anomaly_times, y=anomaly_values, 
                         mode='markers', name="Anomalies"))
st.plotly_chart(fig, use_container_width=True)
```

### 8. Progress Tracking Implementation

**Method 1: Using `st.progress()` and `st.empty()`:**
```python
progress_bar = st.progress(0)
status_text = st.empty()

for step in range(7):
    status_text.text(f"Step {step+1}: Processing...")
    # Process step
    progress_bar.progress((step+1)/7)
    status_text.text(f"Step {step+1}: Complete ✓")
```

**Method 2: Using `st.status()` (Streamlit 1.28+):**
```python
with st.status("Processing...", expanded=True) as status:
    st.write("Step 1: Loading data...")
    # Process step 1
    st.write("Step 2: Feature engineering...")
    # Process step 2
    status.update(label="Complete!", state="complete")
```

### 9. Real-time Streaming Updates

For live data streaming:
```python
import time

placeholder = st.empty()
chunk_processor = stream_service.process_chunks(file_path)

for chunk_result in chunk_processor:
    with placeholder.container():
        st.metric("Anomalies Detected", chunk_result['anomaly_count'])
        st.plotly_chart(chunk_result['chart'])
    time.sleep(0.5)  # Simulate streaming delay
```

## Key Features Implementation

### Progress Tracking
- Use `st.progress()` for overall progress
- Use `st.empty()` containers for step-by-step updates
- Update session state for job status
- Display step names, percentages, and status messages

### Interactive Timelines
- Use Plotly (via `st.plotly_chart()`)
- Full interactivity: zoom, pan, hover, select
- Filter sensors using `st.multiselect()`
- Time range selection using `st.slider()` or date inputs

### Factors & Recommendations
- Display in `st.dataframe()` or `st.table()`
- Use `st.bar_chart()` or Plotly for visualizations
- Collapsible sections using `st.expander()`
- Download options using `st.download_button()`

## Deployment on GCP VM

### Option 1: Simple Deployment (Recommended for Prototype)

1. **SSH into GCP VM**
2. **Install Dependencies:**
   ```bash
   sudo apt update
   sudo apt install python3-pip
   pip3 install streamlit plotly pandas numpy scikit-learn
   ```
3. **Clone/Copy Project:**
   ```bash
   git clone <repo>  # or scp files
   cd anomaly-detection-app
   ```
4. **Run Streamlit:**
   ```bash
   streamlit run app.py --server.port 8501 --server.address 0.0.0.0
   ```
5. **Access:** `http://<VM_IP>:8501`

### Option 2: Production Deployment with systemd

1. **Create systemd service** (`/etc/systemd/system/streamlit-app.service`):
   ```ini
   [Unit]
   Description=Streamlit Anomaly Detection App
   After=network.target

   [Service]
   Type=simple
   User=your-user
   WorkingDirectory=/path/to/anomaly-detection-app
   ExecStart=/usr/bin/streamlit run app.py --server.port 8501
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

2. **Enable and start:**
   ```bash
   sudo systemctl enable streamlit-app
   sudo systemctl start streamlit-app
   ```

### Option 3: With Nginx Reverse Proxy (HTTPS)

1. **Install Nginx:**
   ```bash
   sudo apt install nginx certbot python3-certbot-nginx
   ```

2. **Configure Nginx** (`/etc/nginx/sites-available/streamlit`):
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:8501;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

3. **Enable site and get SSL:**
   ```bash
   sudo ln -s /etc/nginx/sites-available/streamlit /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   sudo certbot --nginx -d your-domain.com
   ```

## Files to Create/Modify

### New Files:
- `app.py` - Main Streamlit application
- `pages/1_🏠_Home.py` - Homepage
- `pages/2_📁_Batch_Processing.py` - Batch processing page
- `pages/3_📊_Data_Stream.py` - Data streaming page
- `services/pipeline_service.py` - Pipeline wrapper with progress
- `services/stream_service.py` - Streaming service
- `utils/progress_tracker.py` - Progress tracking utilities
- `utils/visualization_utils.py` - Chart helper functions

### Modified Files:
- `requirements.txt` - Add streamlit, plotly (if not already present)

### Existing Files (No Changes Needed):
- `config.py`
- `data_exploration.py`
- `feature_engineering.py`
- `statistical_detection.py`
- `ml_detection.py`
- `early_detection.py`
- `visualization.py`

## Advantages of Streamlit Approach

1. **Fast Development**: 2-3 days vs 1-2 weeks
2. **Single Codebase**: All Python, easier to maintain
3. **Direct Integration**: Reuse existing modules without modification
4. **Built-in Features**: File upload, progress bars, charts included
5. **Simple Deployment**: Single process, no build step
6. **Interactive Charts**: Plotly provides full interactivity
7. **Real-time Updates**: Built-in support via `st.empty()` and session state

## Next Steps

1. Set up project structure
2. Create main Streamlit app with navigation
3. Implement homepage with two cards
4. Create batch processing page with file upload
5. Integrate existing Python modules with progress tracking
6. Create data streaming page
7. Add interactive Plotly visualizations
8. Test locally
9. Deploy to GCP VM

## Quick Start Commands

```bash
# Install Streamlit
pip install streamlit plotly

# Run locally
streamlit run app.py

# Run on GCP VM (accessible from outside)
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```
