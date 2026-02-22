"""
Mock Stream Page
Real-time streaming sensor data with live predictions
Fast streaming for live demos
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
from pathlib import Path

from utils.ui_theme import get_css_theme, get_severity_badge_html, get_recommendation_card_html, SEVERITY_COLORS
from utils.mock_stream_generator import MockStreamGenerator
from utils.recommendations_engine import generate_recommendations
from utils.agent_service import get_api_key, stream_gemini_response
from src.model_manager import ModelManager
from src.prediction_service import predict_anomaly_timing
from src.lead_time_predictor import predict_lead_time
from src.severity_classifier import classify_severity
from src.root_cause_analyzer import analyze_root_cause

# Page config
st.set_page_config(
    page_title="Mock Stream",
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

# Hero Section with nav buttons inside the blue box
st.markdown("""
<div id="hero-block" class="hero-section fade-in">
    <div class="hero-badge">Google Cloud · Data & AI Hackathon · Team 4</div>
    <div class="hero-title">Early Detection of Process Excursions</div>
    <div class="hero-subtitle">AI-Powered Anomaly Detection System developed for Methanex</div>
</div>
""", unsafe_allow_html=True)

col_home, col_upload = st.columns(2)
with col_home:
    if st.button("Home", key="nav_home", use_container_width=True):
        st.switch_page("app.py")
with col_upload:
    if st.button("Upload & Analyze", key="nav_upload", use_container_width=True):
        st.switch_page("pages/Upload_Analysis.py")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### Mock Stream - Real-Time Sensor Data")
st.markdown("View real-time streaming sensor data with live anomaly predictions and alerts.")

# Initialize session state
if 'streaming_active' not in st.session_state:
    st.session_state.streaming_active = False
if 'stream_data' not in st.session_state:
    st.session_state.stream_data = pd.DataFrame()
if 'stream_generator' not in st.session_state:
    st.session_state.stream_generator = None
if 'model_manager' not in st.session_state:
    st.session_state.model_manager = None
if 'alerts' not in st.session_state:
    st.session_state.alerts = []
if 'stream_index' not in st.session_state:
    st.session_state.stream_index = 0
if 'pre_generated_data' not in st.session_state:
    st.session_state.pre_generated_data = None
if 'stream_paused_for_anomaly' not in st.session_state:
    st.session_state.stream_paused_for_anomaly = False
if 'stream_pause_snapshot' not in st.session_state:
    st.session_state.stream_pause_snapshot = None
if 'agent_chat_messages_mock' not in st.session_state:
    st.session_state.agent_chat_messages_mock = []
if 'stream_last_predictions' not in st.session_state:
    st.session_state.stream_last_predictions = None
if 'stream_last_processed_data' not in st.session_state:
    st.session_state.stream_last_processed_data = None

# Project root for paths
_project_root = Path(__file__).resolve().parent.parent


def _render_agent_chat_mock():
    """Render the Chat with the Agent section on Mock Stream (in-page form, no fixed blue bar)."""
    api_key = get_api_key()
    if not api_key:
        st.info(
            "To enable the agent, set **GEMINI_API_KEY** in your environment, or add `gemini_api_key` to "
            "Streamlit secrets (e.g. `.streamlit/secrets.toml`)."
        )
        return
    # Chat messages in a compact, in-page layout
    for msg in st.session_state.agent_chat_messages_mock:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    # In-page input (no st.chat_input = no blue ribbon at bottom)
    with st.form("mock_stream_chat_form", clear_on_submit=True):
        prompt = st.text_input(
            "Ask about the stream analysis or get recommendations",
            key="mock_chat_input",
            placeholder="Type your question here..."
        )
        submitted = st.form_submit_button("Send")
    if submitted and (prompt or "").strip():
        prompt = prompt.strip()
        st.session_state.agent_chat_messages_mock.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            stream = stream_gemini_response(
                prompt,
                st.session_state.agent_chat_messages_mock[:-1],
                st.session_state.stream_last_processed_data,
                st.session_state.stream_last_predictions,
                api_key,
            )
            full_response = st.write_stream(stream)
        st.session_state.agent_chat_messages_mock.append({"role": "model", "content": full_response})
        st.rerun()


# Project root for paths
_project_root = Path(__file__).resolve().parent.parent

# Initialize stream generator
if st.session_state.stream_generator is None:
    training_file = _project_root / "Updated Challenge3 Data.csv"
    if training_file.exists():
        st.session_state.stream_generator = MockStreamGenerator(str(training_file))
    else:
        st.session_state.stream_generator = MockStreamGenerator()

# Initialize model manager
if st.session_state.model_manager is None:
    model_manager = ModelManager(model_dir=str(_project_root / "models"))
    if model_manager.load_models():
        st.session_state.model_manager = model_manager
    else:
        st.warning("Models not loaded. Some features may be limited.")

# Stream Controls
st.markdown("### Stream Controls")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("Start Stream", type="primary", disabled=st.session_state.streaming_active):
        st.session_state.streaming_active = True
        st.session_state.stream_data = pd.DataFrame()
        st.session_state.alerts = []
        st.session_state.stream_index = 0
        st.session_state.pre_generated_data = None
        st.session_state.stream_paused_for_anomaly = False
        st.session_state.stream_pause_snapshot = None
        st.rerun()

with col2:
    if st.button("Stop Stream", disabled=not st.session_state.streaming_active):
        st.session_state.streaming_active = False
        st.rerun()

with col3:
    stream_speed = st.selectbox("Stream Speed", ["Demo (0.1s)", "Fast (0.2s)", "Normal (0.5s)", "Slow (1s)"], index=0)
    speed_map = {"Demo (0.1s)": 0.1, "Fast (0.2s)": 0.2, "Normal (0.5s)": 0.5, "Slow (1s)": 1.0}
    interval = speed_map[stream_speed]

with col4:
    hours_to_stream = st.slider("Hours to Stream", 1, 24, 6)

# Status Indicator
if st.session_state.streaming_active:
    st.markdown("""
    <div class="methanex-alert methanex-alert-success">
        <strong>Streaming Active</strong> - Data is being generated and analyzed in real-time
    </div>
    """, unsafe_allow_html=True)
elif st.session_state.stream_paused_for_anomaly:
    st.markdown("""
    <div class="methanex-alert methanex-alert-error">
        <strong>Stream Paused</strong> - Anomaly detected. Review prediction and recommendations below, then click "Start Stream" to run again.
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="methanex-alert">
        <strong>Stream Stopped</strong> - Click "Start Stream" to begin
    </div>
    """, unsafe_allow_html=True)

# Main Display Area
if st.session_state.streaming_active:
    # Pre-generate all data for faster streaming (use demo mode for better flow)
    if st.session_state.pre_generated_data is None:
        with st.spinner("Preparing data stream..."):
            # Use demo_mode=True to create progression: normal -> early warnings -> anomaly
            st.session_state.pre_generated_data = st.session_state.stream_generator.generate_hourly_data(
                hours=hours_to_stream,
                anomaly_probability=0.05,
                demo_mode=True  # Enable demo mode for progression
            )
            # Process the pre-generated data through the model
            if st.session_state.model_manager:
                try:
                    df_processed = st.session_state.model_manager.predict_on_new_data(
                        st.session_state.pre_generated_data, 
                        asset_name='Asset 1'
                    )
                    st.session_state.pre_generated_data = df_processed
                except Exception as e:
                    st.warning(f"Could not process data: {e}")
    
    # Stream data incrementally
    if st.session_state.pre_generated_data is not None:
        # Add next batch of records
        batch_size = 5  # Add 5 records at a time for faster demo
        end_idx = min(st.session_state.stream_index + batch_size, len(st.session_state.pre_generated_data))
        
        if st.session_state.stream_index < len(st.session_state.pre_generated_data):
            new_batch = st.session_state.pre_generated_data.iloc[st.session_state.stream_index:end_idx]
            st.session_state.stream_data = pd.concat([st.session_state.stream_data, new_batch], ignore_index=True)
            st.session_state.stream_index = end_idx
            
            # Check for anomaly and pause stream to show prediction and recommendations
            sd = st.session_state.stream_data
            anomaly_detected = False
            if len(sd) > 0:
                if 'anomaly_combined' in sd.columns and sd['anomaly_combined'].iloc[-1]:
                    anomaly_detected = True
                elif 'anomaly_score_combined' in sd.columns and sd['anomaly_score_combined'].iloc[-1] > 0.7:
                    anomaly_detected = True
            if anomaly_detected and st.session_state.model_manager:
                try:
                    recent_data = sd.tail(min(48, len(sd)))
                    sensor_rankings = st.session_state.model_manager.get_sensor_rankings('Asset 1')
                    timing_pred = predict_anomaly_timing(recent_data, st.session_state.model_manager, sensor_rankings=sensor_rankings)
                    lead_time_pred = predict_lead_time(recent_data, sensor_rankings, st.session_state.model_manager.get_early_detection_history('Asset 1'))
                    latest_score = sd['anomaly_score_combined'].iloc[-1] if 'anomaly_score_combined' in sd.columns else 0.0
                    severity = classify_severity(latest_score)
                    root_cause = analyze_root_cause(recent_data, st.session_state.model_manager, sensor_rankings)
                    recommendations = generate_recommendations(timing_pred, severity['severity_level'], root_cause, lead_time_pred.get('predicted_lead_time_hours'))
                    st.session_state.stream_pause_snapshot = {
                        'timing': timing_pred, 'lead_time': lead_time_pred, 'severity': severity,
                        'root_cause': root_cause, 'recommendations': recommendations
                    }
                except Exception as e:
                    # Always pause on anomaly; use minimal snapshot if full build failed
                    latest_score = sd['anomaly_score_combined'].iloc[-1] if 'anomaly_score_combined' in sd.columns else 0.0
                    severity = classify_severity(latest_score)
                    st.session_state.stream_pause_snapshot = {
                        'timing': {'confidence': 0.0, 'predicted_timestamp': None},
                        'lead_time': {'predicted_lead_time_hours': None, 'confidence': 0.0},
                        'severity': severity,
                        'root_cause': {},
                        'recommendations': [{'title': 'Investigate anomaly', 'priority': severity.get('severity_level', 'Medium'), 'description': 'Anomaly detected. Full analysis unavailable.', 'timeline': 'As soon as possible', 'actions': []}]
                    }
                    if 'stream_pause_error' not in st.session_state:
                        st.session_state.stream_pause_error = None
                    st.session_state.stream_pause_error = str(e)
                # Pause stream in all cases when anomaly detected
                st.session_state.stream_last_predictions = st.session_state.stream_pause_snapshot
                st.session_state.stream_last_processed_data = sd
                st.session_state.streaming_active = False
                st.session_state.stream_paused_for_anomaly = True
                st.rerun()
        else:
            # Reset if we've streamed all data
            st.session_state.stream_index = 0
            st.session_state.stream_data = pd.DataFrame()
    
    # Process data for predictions
    if st.session_state.model_manager and len(st.session_state.stream_data) > 0:
        try:
            # Get last 48 hours for predictions (or all if less)
            recent_data = st.session_state.stream_data.tail(min(48, len(st.session_state.stream_data)))
            
            # Run predictions
            sensor_rankings = st.session_state.model_manager.get_sensor_rankings('Asset 1')
            
            if sensor_rankings is not None and len(sensor_rankings) > 0 and len(recent_data) >= 6:
                timing_pred = predict_anomaly_timing(
                    recent_data,
                    st.session_state.model_manager,
                    sensor_rankings=sensor_rankings
                )
                
                lead_time_pred = predict_lead_time(
                    recent_data,
                    sensor_rankings,
                    st.session_state.model_manager.get_early_detection_history('Asset 1')
                )
                
                # Check for anomalies and generate alerts
                if 'anomaly_score_combined' in st.session_state.stream_data.columns:
                    latest_score = st.session_state.stream_data['anomaly_score_combined'].iloc[-1]
                    severity = classify_severity(latest_score)
                    
                    if latest_score > 0.7 and severity['severity_level'] in ['High', 'Critical']:
                        # Generate alert
                        alert = {
                            'timestamp': datetime.now(),
                            'severity': severity['severity_level'],
                            'score': latest_score,
                            'message': f"Anomaly detected! Severity: {severity['severity_level']}"
                        }
                        # Check if similar alert already exists
                        if not any(a['timestamp'] == alert['timestamp'] and a['severity'] == alert['severity'] 
                                 for a in st.session_state.alerts):
                            st.session_state.alerts.append(alert)
                else:
                    severity = {'severity_level': 'Low', 'severity_score': 0.0}
            else:
                timing_pred = {'confidence': 0.0, 'predicted_timestamp': None}
                lead_time_pred = {'predicted_lead_time_hours': None, 'confidence': 0.0}
                severity = {'severity_level': 'Low', 'severity_score': 0.0}
        except Exception as e:
            timing_pred = {'confidence': 0.0, 'predicted_timestamp': None}
            lead_time_pred = {'predicted_lead_time_hours': None, 'confidence': 0.0}
            severity = {'severity_level': 'Low', 'severity_score': 0.0}
    else:
        timing_pred = {'confidence': 0.0, 'predicted_timestamp': None}
        lead_time_pred = {'predicted_lead_time_hours': None, 'confidence': 0.0}
        severity = {'severity_level': 'Low', 'severity_score': 0.0}
    
    # Keep latest predictions for the agent
    st.session_state.stream_last_predictions = {
        'timing': timing_pred,
        'lead_time': lead_time_pred,
        'severity': severity,
        'root_cause': {},
        'recommendations': []
    }
    st.session_state.stream_last_processed_data = st.session_state.stream_data
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Records Streamed", len(st.session_state.stream_data))
    
    with col2:
        st.markdown(f"**Current Severity:** {get_severity_badge_html(severity['severity_level'])}", unsafe_allow_html=True)
    
    with col3:
        if lead_time_pred.get('predicted_lead_time_hours'):
            st.metric("Predicted Lead Time", f"{lead_time_pred['predicted_lead_time_hours']:.1f} hrs")
        else:
            st.metric("Predicted Lead Time", "N/A")
    
    with col4:
        st.metric("Prediction Confidence", f"{timing_pred.get('confidence', 0)*100:.1f}%")
    
    # Prediction Alert (show when prediction confidence is high)
    if timing_pred.get('confidence', 0) > 0.4 and timing_pred.get('predicted_timestamp'):
        pred_time = timing_pred['predicted_timestamp']
        if hasattr(pred_time, 'strftime'):
            time_str = pred_time.strftime('%Y-%m-%d %H:%M:%S')
        else:
            time_str = str(pred_time)
        
        lead_time_str = f"{lead_time_pred.get('predicted_lead_time_hours', 0):.1f}" if lead_time_pred.get('predicted_lead_time_hours') else "N/A"
        st.markdown(f"""
        <div class="methanex-alert methanex-alert-warning pulse">
            <strong>Anomaly Prediction Active</strong><br>
            Anomaly predicted to occur at: <strong>{time_str}</strong><br>
            Confidence: {timing_pred['confidence']*100:.1f}% | 
            Lead Time: {lead_time_str} hours
        </div>
        """, unsafe_allow_html=True)
        
        # Show recommendations
        if st.session_state.model_manager and len(st.session_state.stream_data) > 12:
            try:
                root_cause = analyze_root_cause(
                    st.session_state.stream_data.tail(48),
                    st.session_state.model_manager,
                    sensor_rankings
                )
                
                recommendations = generate_recommendations(
                    timing_pred,
                    severity['severity_level'],
                    root_cause,
                    lead_time_pred.get('predicted_lead_time_hours')
                )
                
                if recommendations:
                    st.session_state.stream_last_predictions['root_cause'] = root_cause
                    st.session_state.stream_last_predictions['recommendations'] = recommendations
                    st.markdown("### Recommended Actions")
                    for i, rec in enumerate(recommendations[:3], 1):
                        card_html = get_recommendation_card_html(rec, i, include_actions=False)
                        st.markdown(card_html, unsafe_allow_html=True)
                        if rec.get('actions'):
                            with st.expander("Steps to take"):
                                for action in rec['actions']:
                                    st.markdown(f"- {action}")
            except Exception:
                pass
    
    # Alerts
    if st.session_state.alerts:
        st.markdown("### Recent Alerts")
        for alert in st.session_state.alerts[-5:]:  # Show last 5
            alert_color = SEVERITY_COLORS.get(alert['severity'], '#6B7280')
            st.markdown(f"""
            <div class="methanex-alert" style="border-left-color: {alert_color};">
                <strong>{alert['severity']}</strong> - {alert['message']} (Score: {alert['score']:.2f})
                <br><small>{alert['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}</small>
            </div>
            """, unsafe_allow_html=True)
    
    # Visualizations
    st.markdown("### Real-Time Visualizations")
    
    if len(st.session_state.stream_data) > 0:
        # Time series chart - Show multiple sensors
        fig = go.Figure()
        
        # Plot multiple sensors to show comprehensive monitoring
        key_sensors = [
            'Asset 1 HP - Disch Press Value',
            'Asset 1 HP - Pressure & Ratio Value',
            'Asset 1T - Speed Value',
            'Asset 1T Steam Inlet flow Value',
            'Asset 2 - Disch Press Value',
            'Asset 2T - Speed Value'
        ]
        
        colors = ['#1E3A8A', '#3B82F6', '#60A5FA', '#10B981', '#F59E0B', '#EF4444']
        
        for i, sensor in enumerate(key_sensors):
            if sensor in st.session_state.stream_data.columns:
                fig.add_trace(go.Scatter(
                    x=st.session_state.stream_data['Timestamp'],
                    y=st.session_state.stream_data[sensor],
                    mode='lines',
                    name=sensor,
                    line=dict(color=colors[i % len(colors)], width=2),
                    visible='legendonly' if i > 2 else True  # Show first 3 by default
                ))
        
        fig.update_layout(
            title='Real-Time Multi-Sensor Monitoring',
            xaxis_title='Timestamp',
            yaxis_title='Sensor Value',
            height=400,
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Status indicator based on stream progress
        progress_pct = (st.session_state.stream_index / len(st.session_state.pre_generated_data) * 100) if st.session_state.pre_generated_data is not None else 0
        
        if progress_pct < 30:
            st.info("**Phase 1: Normal Operation** - All sensors operating within normal parameters.")
        elif progress_pct < 70:
            st.warning("**Phase 2: Early Warning Indicators Detected** - Some sensors showing deviations. System monitoring for potential anomalies.")
        else:
            st.error("**Phase 3: Anomaly Period** - Significant deviations detected. Anomaly prediction active.")
        
        # Anomaly score timeline
        if 'anomaly_score_combined' in st.session_state.stream_data.columns:
            fig2 = go.Figure()
            
            fig2.add_trace(go.Scatter(
                x=st.session_state.stream_data['Timestamp'],
                y=st.session_state.stream_data['anomaly_score_combined'],
                mode='lines+markers',
                name='Anomaly Score',
                line=dict(color='#EF4444', width=2),
                marker=dict(size=4)
            ))
            
            # Add threshold line
            fig2.add_hline(y=0.7, line_dash="dash", line_color="orange", 
                          annotation_text="High Threshold")
            
            fig2.update_layout(
                title='Anomaly Score Timeline',
                xaxis_title='Timestamp',
                yaxis_title='Anomaly Score',
                height=300
            )
            
            st.plotly_chart(fig2, use_container_width=True)
    
    # Chat with the Agent (bottom of Mock Stream when streaming)
    st.markdown("---")
    st.markdown("#### Chat with the Agent")
    st.markdown("Ask questions about the stream analysis or get recommendations. Responses are streamed.")
    _render_agent_chat_mock()
    
    # Auto-refresh with minimal delay
    time.sleep(interval)
    st.rerun()

else:
    # Paused due to anomaly: show prediction and recommendations
    if st.session_state.stream_paused_for_anomaly and st.session_state.stream_pause_snapshot:
        snap = st.session_state.stream_pause_snapshot
        if getattr(st.session_state, 'stream_pause_error', None):
            st.warning(f"Stream paused for anomaly. Some analysis failed: {st.session_state.stream_pause_error}")
            st.session_state.stream_pause_error = None  # clear after showing once
        st.markdown("### Prediction Around Anomaly")
        
        col1, col2 = st.columns(2)
        with col1:
            timing = snap.get('timing', {})
            if timing.get('predicted_timestamp'):
                pred_time = timing['predicted_timestamp']
                time_str = pred_time.strftime('%Y-%m-%d %H:%M:%S') if hasattr(pred_time, 'strftime') else str(pred_time)
                st.metric("Predicted Anomaly Time", time_str)
                st.markdown(f"**Confidence:** {timing.get('confidence', 0)*100:.1f}%")
            lead_time = snap.get('lead_time', {})
            if lead_time.get('predicted_lead_time_hours'):
                st.metric("Lead Time", f"{lead_time['predicted_lead_time_hours']:.1f} hours")
        with col2:
            severity = snap.get('severity', {})
            st.markdown(f"**Severity:** {get_severity_badge_html(severity.get('severity_level', 'Low'))}", unsafe_allow_html=True)
        
        st.markdown("### Recommended Actions")
        recommendations = snap.get('recommendations') or []
        if recommendations:
            rec_cols = st.columns(2)
            for i, rec in enumerate(recommendations, 1):
                with rec_cols[(i - 1) % 2]:
                    card_html = get_recommendation_card_html(rec, i, include_actions=False)
                    st.markdown(card_html, unsafe_allow_html=True)
                    if rec.get('actions'):
                        with st.expander("Steps to take"):
                            for action in rec['actions']:
                                st.markdown(f"- {action}")
        st.info("Click **Start Stream** above to run a new stream.")
    
    # Static view when not streaming (and not paused)
    elif len(st.session_state.stream_data) > 0:
        st.markdown("### Historical Data View")
        
        # Show summary
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Records", len(st.session_state.stream_data))
        
        with col2:
            if 'anomaly_combined' in st.session_state.stream_data.columns:
                anomalies = st.session_state.stream_data['anomaly_combined'].sum()
                st.metric("Anomalies Detected", int(anomalies))
            else:
                st.metric("Anomalies Detected", "N/A")
        
        with col3:
            if 'Timestamp' in st.session_state.stream_data.columns:
                time_range = st.session_state.stream_data['Timestamp'].max() - st.session_state.stream_data['Timestamp'].min()
                st.metric("Time Range", f"{time_range.total_seconds()/3600:.1f} hours")
        
        # Visualization
        if len(st.session_state.stream_data) > 0:
            fig = go.Figure()
            
            key_sensors = ['Asset 1 HP - Disch Press Value', 'Asset 1T - Speed Value']
            colors = ['#1E3A8A', '#3B82F6']
            
            for i, sensor in enumerate(key_sensors):
                if sensor in st.session_state.stream_data.columns:
                    fig.add_trace(go.Scatter(
                        x=st.session_state.stream_data['Timestamp'],
                        y=st.session_state.stream_data[sensor],
                        mode='lines',
                        name=sensor,
                        line=dict(color=colors[i], width=2)
                    ))
            
            fig.update_layout(
                title='Historical Sensor Data',
                xaxis_title='Timestamp',
                yaxis_title='Sensor Value',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Click 'Start Stream' to begin generating and analyzing real-time sensor data.")
    
    # Chat with the Agent when stream is stopped (with or without historical data)
    st.markdown("---")
    st.markdown("#### Chat with the Agent")
    st.markdown("Ask questions about the stream analysis or get recommendations.")
    _render_agent_chat_mock()
