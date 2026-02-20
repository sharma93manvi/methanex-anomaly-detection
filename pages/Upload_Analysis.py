"""
Upload & Analysis Page
Allows users to upload sensor data and get comprehensive predictions
Professional design without icons
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

from utils.ui_theme import get_css_theme, get_severity_badge_html, get_recommendation_card_html, SEVERITY_COLORS
from src.model_manager import ModelManager
from src.prediction_service import predict_anomaly_timing
from src.lead_time_predictor import predict_lead_time
from src.severity_classifier import classify_severity_from_dataframe, classify_severity
from src.root_cause_analyzer import analyze_root_cause
from utils.recommendations_engine import generate_recommendations, format_recommendations_for_display
from utils.agent_service import get_api_key, stream_gemini_response

# Page config
st.set_page_config(
    page_title="Upload & Analysis",
    page_icon=None,
    layout="wide"
)

# Apply theme
st.markdown(get_css_theme(), unsafe_allow_html=True)

# Hide sidebar and sidebar toggle arrow
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        display: none;
    }
    [data-testid="collapsedControl"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# Top Navigation
col_nav1, col_nav2, col_nav3 = st.columns([3, 1, 1])

with col_nav1:
    st.markdown("### Methanex Anomaly Detection System")

with col_nav2:
    if st.button("Home", key="nav_home", use_container_width=True):
        st.switch_page("app.py")

with col_nav3:
    if st.button("Mock Stream", key="nav_stream", use_container_width=True):
        st.switch_page("pages/Mock_Stream.py")

st.markdown("---")

# Hero Section (consistent across app)
st.markdown("""
<div class="hero-section fade-in">
    <div class="hero-title">Early Detection of Process Excursions</div>
    <div class="hero-subtitle">AI-Powered Anomaly Detection System for Industrial Sensor Data</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### Upload Sensor Data & Analysis")
st.markdown("Upload hourly sensor data files to get comprehensive anomaly predictions and recommendations.")

# Initialize session state
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'predictions' not in st.session_state:
    st.session_state.predictions = None
if 'agent_chat_messages' not in st.session_state:
    st.session_state.agent_chat_messages = []


def _render_agent_chat(key_suffix="upload"):
    """Render the Chat with the Agent section (shared by both tabs). key_suffix must be unique per tab."""
    api_key = get_api_key()
    if not api_key:
        st.info(
            "To enable the agent, set **GEMINI_API_KEY** in your environment, or add `gemini_api_key` to "
            "Streamlit secrets (e.g. `.streamlit/secrets.toml`)."
        )
        return
    for msg in st.session_state.agent_chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    if prompt := st.chat_input("Ask about model outputs or the detection system...", key=f"agent_chat_input_{key_suffix}"):
        st.session_state.agent_chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            stream = stream_gemini_response(
                prompt,
                st.session_state.agent_chat_messages[:-1],
                st.session_state.processed_data,
                st.session_state.predictions,
                api_key,
            )
            full_response = st.write_stream(stream)
        st.session_state.agent_chat_messages.append({"role": "model", "content": full_response})
        st.rerun()


# Test Files Section
st.markdown("### Quick Test Files")
st.markdown("Select a pre-generated test file to quickly test the system:")

# Sensible display names for test files (filename -> label)
TEST_FILE_LABELS = {
    "normal_30days.csv": "Normal operation (30 days)",
    "early_warning_30days.csv": "Early warning scenario (30 days)",
    "high_severity_30days.csv": "High severity anomaly (30 days)",
}

# Resolve paths relative to project root (where app.py lives)
_project_root = Path(__file__).resolve().parent.parent
test_files_dir = _project_root / "test_data"
if test_files_dir.exists():
    # Deduplicate by path and sort for consistent order
    seen = set()
    test_files = []
    for f in sorted(test_files_dir.glob("*.csv"), key=lambda p: p.name):
        if f.resolve() not in seen:
            seen.add(f.resolve())
            test_files.append(f)
    # Build options: [None] + list of (display_label, filename)
    file_options = ["None"]
    label_to_path = {"None": None}
    for f in test_files:
        label = TEST_FILE_LABELS.get(f.name, f.name)
        file_options.append(label)
        label_to_path[label] = f
    
    if len(file_options) > 1:
        selected_label = st.selectbox(
            "Choose a test file:",
            file_options,
            key="test_file_selector"
        )
        
        if selected_label != "None":
            test_file_path = label_to_path[selected_label]
            if test_file_path and st.button("Load Test File", key="load_test"):
                st.session_state.uploaded_file = str(test_file_path)
                st.session_state.test_file_loaded = True
                st.rerun()
    else:
        st.info("No test files found. Generate them using the mock batch generator.")
else:
    st.info("Test data directory not found.")

st.markdown("---")

# Main Content
tab1, tab2 = st.tabs(["Upload Data", "Results"])

with tab1:
    st.markdown("### Upload Your Sensor Data")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a CSV file with hourly sensor data",
        type=['csv'],
        help="File should contain Timestamp column and sensor readings"
    )
    
    if uploaded_file is not None:
        st.session_state.uploaded_file = uploaded_file
    
    # Or use test file
    if st.session_state.uploaded_file:
        if isinstance(st.session_state.uploaded_file, str):
            file_path = st.session_state.uploaded_file
            file_name = Path(file_path).name
        else:
            file_path = None
            file_name = st.session_state.uploaded_file.name
        
        st.success(f"File loaded: **{file_name}**")
        
        # Preview data
        with st.expander("Preview Data", expanded=False):
            try:
                if file_path:
                    path_obj = Path(file_path)
                    if not path_obj.exists():
                        path_obj = _project_root / "test_data" / path_obj.name
                    df_preview = pd.read_csv(path_obj, nrows=10, encoding="utf-8")
                    df_preview.columns = df_preview.columns.str.strip()
                else:
                    df_preview = pd.read_csv(st.session_state.uploaded_file, nrows=10)
                    df_preview.columns = df_preview.columns.str.strip()
                st.dataframe(df_preview)
            except Exception as e:
                st.error(f"Error reading file: {e}")
        
        # Process button
        if st.button("Process Data & Generate Predictions", type="primary", use_container_width=True):
            with st.spinner("Processing data and generating predictions..."):
                try:
                    # Load data (reset file position if file-like so we read full file after preview)
                    if file_path:
                        path_obj = Path(file_path)
                        if not path_obj.exists():
                            # Resolve test_data path relative to project root (handles different cwd)
                            fallback = _project_root / "test_data" / path_obj.name
                            if fallback.exists():
                                path_obj = fallback
                            elif (_project_root / path_obj).exists():
                                path_obj = _project_root / path_obj
                            else:
                                raise FileNotFoundError(f"File not found: {file_path}")
                        df = pd.read_csv(path_obj, encoding="utf-8")
                        df.columns = df.columns.str.strip()
                    else:
                        up = st.session_state.uploaded_file
                        if hasattr(up, 'seek'):
                            up.seek(0)
                        df = pd.read_csv(up)
                        df.columns = df.columns.str.strip()
                    
                    # Ensure Timestamp column
                    if 'Timestamp' not in df.columns:
                        st.error("Error: CSV file must contain a 'Timestamp' column")
                        st.stop()
                    
                    # Validate required sensor columns for Asset 1 inference
                    required_cols = ['Asset 1 HP - Disch Press Value', 'target Value']
                    missing = [c for c in required_cols if c not in df.columns]
                    if missing:
                        st.error(f"Error: CSV is missing required columns: {', '.join(missing)}. Expected sensor columns matching the training data schema.")
                        st.stop()
                    
                    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
                    df = df.sort_values('Timestamp').reset_index(drop=True)
                    
                    # Load models (from project root so it works regardless of cwd)
                    model_manager = ModelManager(model_dir=str(_project_root / "models"))
                    models_loaded = model_manager.load_models()
                    
                    if not models_loaded:
                        st.warning("Models not found. Training models on uploaded data...")
                        st.info("For full functionality, please run the main pipeline first to train models.")
                        st.stop()
                    
                    # Run inference
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    status_text.markdown("**Step 1/5**: Running anomaly detection...")
                    progress_bar.progress(20)
                    
                    df_processed = model_manager.predict_on_new_data(df, asset_name='Asset 1')
                    
                    status_text.markdown("**Step 2/5**: Classifying severity...")
                    progress_bar.progress(40)
                    
                    df_processed = classify_severity_from_dataframe(df_processed)
                    
                    status_text.markdown("**Step 3/5**: Predicting anomaly timing...")
                    progress_bar.progress(60)
                    
                    sensor_rankings = model_manager.get_sensor_rankings('Asset 1')
                    
                    # Use recent data for predictions (last 48 hours or all if less)
                    recent_data = df_processed.tail(min(48, len(df_processed)))
                    
                    timing_prediction = predict_anomaly_timing(
                        recent_data,
                        model_manager,
                        sensor_rankings=sensor_rankings
                    )
                    
                    status_text.markdown("**Step 4/5**: Predicting lead time...")
                    progress_bar.progress(80)
                    
                    lead_time_prediction = predict_lead_time(
                        recent_data,
                        sensor_rankings,
                        model_manager.get_early_detection_history('Asset 1')
                    )
                    
                    status_text.markdown("**Step 5/5**: Analyzing root cause...")
                    progress_bar.progress(90)
                    
                    # For root cause, use recent data or all data if anomalies detected
                    analysis_data = recent_data if len(recent_data) >= 12 else df_processed.tail(12)
                    root_cause_analysis = analyze_root_cause(
                        analysis_data,
                        model_manager,
                        sensor_rankings
                    )
                    
                    # Severity from batch peak (max score), not just last row, so anomaly periods
                    # in the middle of the file (e.g. high_severity_30days) are reflected correctly
                    if 'anomaly_score_combined' in df_processed.columns:
                        peak_score = float(df_processed['anomaly_score_combined'].max())
                        latest_score = float(df_processed['anomaly_score_combined'].iloc[-1])
                    else:
                        peak_score = 0.0
                        latest_score = 0.0
                    latest_severity = df_processed['severity_level'].iloc[-1] if 'severity_level' in df_processed.columns else 'Low'
                    severity_result = classify_severity(peak_score)
                    
                    # Generate recommendations
                    recommendations = generate_recommendations(
                        timing_prediction,
                        severity_result['severity_level'],
                        root_cause_analysis,
                        lead_time_prediction.get('predicted_lead_time_hours')
                    )
                    
                    progress_bar.progress(100)
                    status_text.markdown("**Processing Complete!**")
                    
                    # Store results
                    st.session_state.processed_data = df_processed
                    st.session_state.predictions = {
                        'timing': timing_prediction,
                        'lead_time': lead_time_prediction,
                        'severity': severity_result,
                        'root_cause': root_cause_analysis,
                        'recommendations': recommendations
                    }
                    
                    st.success("Data processed successfully! View results in the Results tab.")
                    
                except Exception as e:
                    st.error(f"Error processing data: {e}")
                    st.exception(e)

    # Chat with the Agent (bottom of Upload Data tab)
    st.markdown("---")
    st.markdown("#### Chat with the Agent")
    st.markdown("Ask questions about the model outputs or the anomaly detection system. Responses are streamed for a natural conversation.")
    _render_agent_chat("upload")

with tab2:
    st.markdown("### Analysis Results")
    
    if st.session_state.processed_data is None or st.session_state.predictions is None:
        st.info("Please upload and process data in the 'Upload Data' tab first.")
    else:
        df_processed = st.session_state.processed_data
        predictions = st.session_state.predictions
        
        # Summary Metrics
        st.markdown("#### Summary Metrics")
        
        # Check for current anomalies
        # Consider "no anomalies" if very few are detected (less than 1% of records)
        # This accounts for ML model's contamination rate
        anomalies = df_processed['anomaly_combined'].sum() if 'anomaly_combined' in df_processed.columns else 0
        anomaly_rate = anomalies / len(df_processed) if len(df_processed) > 0 else 0
        has_current_anomalies = anomaly_rate > 0.01  # More than 1% = significant anomalies
        
        # Check for future predictions
        has_future_prediction = (
            predictions['timing'].get('predicted_timestamp') is not None and
            predictions['timing'].get('confidence', 0) > 0.3
        )
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if has_current_anomalies:
                st.metric("Current Anomalies Detected", f"{int(anomalies)}", delta=None)
            else:
                st.metric("Current Anomalies Detected", "0", delta="No anomalies", delta_color="normal")
        
        with col2:
            if has_future_prediction:
                # Use lead_time predictor value, or fall back to timing prediction's lead_time_hours
                lead_time = predictions['lead_time'].get('predicted_lead_time_hours')
                if lead_time is None:
                    lead_time = predictions['timing'].get('lead_time_hours')
                if lead_time is not None:
                    st.metric("Anomaly Predicted In", f"{lead_time:.1f} hours", delta="Future anomaly predicted", delta_color="off")
                else:
                    st.metric("Anomaly Predicted In", "N/A")
            else:
                st.metric("Future Anomaly Prediction", "None", delta="No future anomalies predicted", delta_color="normal")
        
        with col3:
            if has_future_prediction:
                confidence = predictions['timing'].get('confidence', 0.0)
                st.metric("Prediction Confidence", f"{confidence*100:.1f}%")
            else:
                st.metric("Prediction Confidence", "N/A")
        
        with col4:
            severity_level = predictions['severity']['severity_level']
            if not has_current_anomalies and not has_future_prediction:
                st.markdown(f"**Status:** <span style='color: green; font-weight: bold;'>Normal Operation</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"**Severity:** {get_severity_badge_html(severity_level)}", unsafe_allow_html=True)
        
        # Status Message
        if not has_current_anomalies and not has_future_prediction:
            st.markdown("""
            <div class="methanex-alert methanex-alert-success">
                <strong>System Operating Normally</strong><br>
                All sensor readings are within normal operating parameters. 
                <strong>No current anomalies detected</strong> and <strong>no future anomalies predicted</strong>.
                Continue normal monitoring and scheduled maintenance procedures.
            </div>
            """, unsafe_allow_html=True)
        elif not has_current_anomalies and has_future_prediction:
            st.markdown("""
            <div class="methanex-alert methanex-alert-warning">
                <strong>Future Anomaly Predicted</strong> - While no current anomalies are detected, 
                early warning indicators suggest an anomaly may occur in the near future. Review predictions and recommendations below.
            </div>
            """, unsafe_allow_html=True)
        elif has_current_anomalies:
            st.markdown("""
            <div class="methanex-alert methanex-alert-error">
                <strong>Anomalies Detected</strong> - Current anomalies have been identified in the sensor data. 
                Review the analysis below for details and recommendations.
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Detailed Results Tabs
        result_tabs = st.tabs([
            "Anomaly Timing",
            "Lead Time",
            "Severity",
            "Root Cause",
            "Recommendations"
        ])
        
        with result_tabs[0]:  # Anomaly Timing
            st.markdown("### Anomaly Timing Prediction")
            
            timing = predictions['timing']
            
            if timing.get('predicted_timestamp') and timing.get('confidence', 0) > 0.3:
                col1, col2 = st.columns(2)
                
                with col1:
                    pred_time = timing['predicted_timestamp']
                    if hasattr(pred_time, 'strftime'):
                        time_str = pred_time.strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        time_str = str(pred_time)
                    
                    st.markdown(f"""
                    **Predicted Anomaly Time:**  
                    {time_str}
                    
                    **Confidence:** {timing['confidence']*100:.1f}%  
                    **Method:** {timing['method'].replace('_', ' ').title()}
                    """)
                    
                    if timing.get('lead_time_hours'):
                        st.markdown(f"**Hours Until Anomaly:** {timing['lead_time_hours']:.1f} hours")
                
                with col2:
                    if timing.get('early_indicators'):
                        st.markdown("**Early Warning Indicators:**")
                        for indicator in timing['early_indicators'][:5]:
                            sensor_name = indicator['sensor'].replace('anomaly_', '').replace('_', ' ').title()
                            st.markdown(f"- **{sensor_name}**: {indicator.get('deviation', 0):.2f}σ deviation")
                    else:
                        st.info("No specific early indicators identified.")
            else:
                st.info("**No Future Anomaly Predicted** - Based on current sensor readings, no anomalies are expected in the near future. System is operating normally.")
        
        with result_tabs[1]:  # Lead Time
            st.markdown("### Lead Time Prediction")
            
            lead_time = predictions['lead_time']
            timing = predictions['timing']
            has_lead_time_value = lead_time.get('predicted_lead_time_hours') is not None
            has_timing_fallback = (
                timing.get('lead_time_hours') is not None and
                timing.get('predicted_timestamp') and
                timing.get('confidence', 0) > 0.3
            )
            
            if has_lead_time_value:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric(
                        "Predicted Lead Time",
                        f"{lead_time['predicted_lead_time_hours']:.1f} hours"
                    )
                    
                    if lead_time.get('confidence_range'):
                        min_h, max_h = lead_time['confidence_range']
                        st.markdown(f"**Confidence Range:** {min_h:.1f} - {max_h:.1f} hours")
                    
                    st.markdown(f"**Confidence:** {lead_time['confidence']*100:.1f}%")
                
                with col2:
                    if lead_time.get('contributing_sensors'):
                        st.markdown("**Early Warning Indicators (contributing sensors):**")
                        st.caption("Sensors showing deviation that historically precede anomalies.")
                        for sensor in lead_time['contributing_sensors'][:5]:
                            st.markdown(f"- {sensor['sensor']}: {sensor.get('confidence', 0)*100:.1f}% confidence")
                    else:
                        st.info("No contributing sensors identified for this prediction.")
            elif has_timing_fallback:
                # Use timing prediction when lead_time predictor is empty (e.g. no sensor rankings)
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        "Predicted Lead Time",
                        f"{timing['lead_time_hours']:.1f} hours"
                    )
                    st.markdown(f"**Confidence:** {timing.get('confidence', 0)*100:.1f}%")
                    st.markdown(f"**Source:** Anomaly Timing ({timing.get('method', 'forecasting').replace('_', ' ').title()} method)")
                with col2:
                    if timing.get('early_indicators'):
                        st.markdown("**Early Warning Indicators:**")
                        st.caption("Sensors with elevated deviation in recent data (from model's early-warning sensor list).")
                        for ind in timing['early_indicators'][:5]:
                            name = ind.get('sensor', 'Unknown')
                            dev = ind.get('deviation', 0)
                            st.markdown(f"- {name}: {dev:.2f}σ deviation")
                    else:
                        st.markdown("**Early indicators:**")
                        st.caption("Identified from the model's ranked early-warning sensors when they show deviation in the current data. None flagged for this run; lead time is from trend/forecasting.")
            else:
                st.info("No lead time prediction available.")
        
        with result_tabs[2]:  # Severity
            st.markdown("### Severity Classification")
            
            severity = predictions['severity']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Severity Level:** {get_severity_badge_html(severity['severity_level'])}", unsafe_allow_html=True)
                st.markdown(f"**Severity Score:** {severity['severity_score']:.2f}")
            
            with col2:
                if severity.get('factors'):
                    st.markdown("**Contributing Factors:**")
                    for factor in severity['factors']:
                        st.markdown(f"- {factor}")
        
        with result_tabs[3]:  # Root Cause
            st.markdown("### Root Cause Analysis")
            
            root_cause = predictions['root_cause']
            
            if root_cause.get('primary_cause'):
                st.markdown(f"""
                **Primary Cause:** {root_cause['primary_cause'].get('sensor', 'Unknown')}  
                **Confidence:** {root_cause['confidence']*100:.1f}%
                """)
                
                if root_cause.get('contributing_factors'):
                    st.markdown("**Contributing Factors:**")
                    for factor in root_cause['contributing_factors'][:5]:
                        st.markdown(f"- {factor.get('sensor', 'Unknown')}: {factor.get('score', 0):.3f}")
            else:
                st.info("No root cause identified.")
        
        with result_tabs[4]:  # Recommendations
            st.markdown("### Actionable Recommendations")
            
            recommendations = predictions['recommendations']
            
            if recommendations:
                # Compact card grid: 2 columns so users can scan without long scroll
                n = len(recommendations)
                cols = st.columns(2)
                for i, rec in enumerate(recommendations, 1):
                    col = cols[(i - 1) % 2]
                    with col:
                        # Card summary (no actions in HTML to keep it short)
                        card_html = get_recommendation_card_html(rec, i, include_actions=False)
                        st.markdown(card_html, unsafe_allow_html=True)
                        # Actions in expander so main view stays compact
                        actions = rec.get('actions') or []
                        if actions:
                            with st.expander("Steps to take", expanded=(i == 1 and n <= 4)):
                                for action in actions:
                                    st.markdown(f"- {action}")
            else:
                if not has_current_anomalies and not has_future_prediction:
                    st.info("""
                    **System Operating Normally**
                    
                    No recommendations at this time. Continue normal monitoring and scheduled maintenance procedures.
                    """)
                else:
                    st.info("No specific recommendations generated. Review the analysis above for details.")
        
        # Visualizations
        st.markdown("---")
        st.markdown("### Visualizations")
        
        if 'Timestamp' in df_processed.columns and 'anomaly_score_combined' in df_processed.columns:
            # Time series with anomalies
            fig = go.Figure()
            
            # Normal data
            normal_data = df_processed[df_processed['anomaly_combined'] == False] if 'anomaly_combined' in df_processed.columns else df_processed
            if len(normal_data) > 0:
                fig.add_trace(go.Scatter(
                    x=normal_data['Timestamp'],
                    y=normal_data['anomaly_score_combined'],
                    mode='markers',
                    name='Normal',
                    marker=dict(color='lightblue', size=2, opacity=0.5)
                ))
            
            # Anomaly data
            if 'anomaly_combined' in df_processed.columns:
                anomaly_data = df_processed[df_processed['anomaly_combined'] == True]
                if len(anomaly_data) > 0:
                    fig.add_trace(go.Scatter(
                        x=anomaly_data['Timestamp'],
                        y=anomaly_data['anomaly_score_combined'],
                        mode='markers',
                        name='Anomaly',
                        marker=dict(color='red', size=4)
                    ))
            
            fig.update_layout(
                title='Anomaly Scores Over Time',
                xaxis_title='Timestamp',
                yaxis_title='Anomaly Score',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)

    # Chat with the Agent (bottom of Results tab; shown with or without results)
    st.markdown("---")
    st.markdown("#### Chat with the Agent")
    st.markdown("Ask questions about the model outputs or the anomaly detection system. Responses are streamed for a natural conversation.")
    _render_agent_chat("results")
