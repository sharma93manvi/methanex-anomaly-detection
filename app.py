"""
Streamlit Web Application for Anomaly Detection System
Main entry point for the web application (Homepage)
Professional design without icons
"""

import streamlit as st
from utils.ui_theme import get_css_theme, COLORS

# Page configuration
st.set_page_config(
    page_title="Methanex Anomaly Detection System",
    page_icon=None,  # No icon
    layout="wide",
    initial_sidebar_state="collapsed"  # Collapse sidebar
)

# Apply Methanex theme
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

# Initialize session state
if 'processing_results' not in st.session_state:
    st.session_state.processing_results = None
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0
if 'processing_status' not in st.session_state:
    st.session_state.processing_status = 'idle'
if 'demo_data_loaded' not in st.session_state:
    st.session_state.demo_data_loaded = False
if 'model_manager' not in st.session_state:
    st.session_state.model_manager = None

# Load demo data on first run
if not st.session_state.demo_data_loaded:
    try:
        from utils.demo_data_loader import load_demo_results
        demo_results = load_demo_results()
        if demo_results.get('demo_data_loaded', False):
            st.session_state.processing_results = demo_results
            st.session_state.demo_data_loaded = True
    except Exception:
        pass

# Top Navigation Bar
col_nav1, col_nav2, col_nav3 = st.columns([3, 1, 1])

with col_nav1:
    st.markdown("### Methanex Anomaly Detection System")

with col_nav2:
    if st.button("Upload & Analyze", key="nav_upload", use_container_width=True, type="primary"):
        st.switch_page("pages/Upload_Analysis.py")

with col_nav3:
    if st.button("Mock Stream", key="nav_stream", use_container_width=True, type="secondary"):
        st.switch_page("pages/Mock_Stream.py")

st.markdown("---")

# Hero Section
st.markdown(f"""
<div class="hero-section fade-in">
    <div class="hero-title">Early Detection of Process Excursions</div>
    <div class="hero-subtitle">AI-Powered Anomaly Detection System for Industrial Sensor Data</div>
</div>
""", unsafe_allow_html=True)

# Main Options - Two Large Cards
st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("""
    <div class="methanex-card methanex-card-hero fade-in card-touch" style="text-align: center; cursor: pointer;">
        <h2 class="card-title">Upload Sensor Data</h2>
        <p class="card-desc">
            Upload hourly sensor data files and get comprehensive anomaly predictions
        </p>
        <div class="card-features">
            Anomaly Timing Prediction<br>
            Lead Time Analysis<br>
            Severity Classification<br>
            Root Cause Analysis<br>
            Actionable Recommendations
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Upload & Analyze Data", key="upload_btn", use_container_width=True, 
                 type="primary"):
        st.switch_page("pages/Upload_Analysis.py")

with col2:
    st.markdown("""
    <div class="methanex-card methanex-card-hero fade-in card-touch" style="text-align: center; cursor: pointer;">
        <h2 class="card-title">View Mock Stream</h2>
        <p class="card-desc">
            View real-time streaming sensor data with live predictions
        </p>
        <div class="card-features">
            Real-time Data Streaming<br>
            Live Anomaly Detection<br>
            Instant Predictions<br>
            Interactive Visualizations<br>
            Alert Notifications
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("View Mock Stream", key="stream_btn", use_container_width=True, 
                 type="primary"):
        st.switch_page("pages/Mock_Stream.py")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")

# System Overview
with st.expander("System Overview", expanded=False):
    st.markdown("""
    ### System Architecture
    
    **Detection Methods:**
    - Statistical Methods: Z-scores, percentiles, moving averages
    - ML Methods: Isolation Forest, Autoencoder, LSTM
    - Ensemble Approach: Combines multiple methods for robust detection
    
    **Key Features:**
    - 170+ engineered features from 19 original sensors
    - Two-tier notification system (Early Warning + Priority Escalation)
    - Early detection analysis with sensor ranking
    - Comprehensive visualization and reporting
    - Predictive capabilities for future anomalies
    
    **Performance:**
    - 18-28 hour average lead time for early warnings
    - High accuracy anomaly detection
    - Real-time and batch processing modes
    """)
