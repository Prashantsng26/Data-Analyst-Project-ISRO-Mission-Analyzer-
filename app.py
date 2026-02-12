import streamlit as st
import os
import sys

# --- Initial Setup & Page Config ---
# This MUST be the very first Streamlit command
st.set_page_config(
    page_title="ISRO Mission Analyzer",
    page_icon="🚀",
    layout="wide"
)

# --- Diagnostic Import Block ---
# We move EVERY import inside here so we can catch startup failures
try:
    print("DEBUG: Starting import sequence...")
    import requests
    import pandas as pd
    import numpy as np
    import plotly.express as px
    import plotly.graph_objects as go
    import base64
    import traceback

    # Ensure the current directory is in sys.path for backend imports
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    print(f"DEBUG: Current directory defined as {current_dir}")

    # Backend Imports
    from backend.data_loader import load_data
    from backend.eda import get_growth_trend, get_success_rates, get_strategic_focus, get_orbit_complexity
    from backend.ml_model import train_model, get_model_metrics, predict_success, get_feature_importance
    print("DEBUG: Backend modules loaded successfully.")

except Exception as e:
    st.error("❌ Critical Startup Error: Failed to load dependencies or backend modules.")
    st.info("This is usually caused by a 'ModuleNotFoundError' or a version conflict in requirements.txt.")
    st.warning("Check the 'Manage App' -> 'Logs' section on your Streamlit Cloud dashboard for details.")
    st.exception(e)
    # Print to stdout so it shows in Streamlit Cloud logs
    print(f"FATAL ERROR DURING IMPORT: {str(e)}")
    traceback.print_exc()
    st.stop()

# Configuration
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api")

# --- Data & Model Initialization (Streamlit Native) ---
@st.cache_data
def get_isro_data():
    try:
        return load_data()
    except Exception as e:
        print(f"ERROR in get_isro_data: {e}")
        return None

@st.cache_resource
def get_trained_model(_df):
    try:
        if _df is not None and not _df.empty:
            pipeline, metrics = train_model(_df)
            return pipeline, metrics
    except Exception as e:
        print(f"ERROR in get_trained_model: {e}")
    return None, {}

# Initialize Data and Model with Error Handling
try:
    with st.spinner("Initializing ISRO Data and Model..."):
        df = get_isro_data()
        if df is None or df.empty:
            st.error("⚠️ Failed to load mission data. Please check if 'backend/isro-missions.sql' is present.")
            st.stop()
        
        # Initialize Model & Metrics
        model_obj, model_metrics = get_trained_model(df)
        if model_obj is None:
            st.warning("⚠️ Machine Learning model could not be initialized. Prediction features might be limited.")
except Exception as e:
    st.error(f"❌ Application Initialization Error: {str(e)}")
    st.stop()

# --- Custom CSS for Space Theme ---
def get_base64_of_bin_file(bin_file):
    try:
        if os.path.exists(bin_file):
            with open(bin_file, 'rb') as f:
                data = f.read()
            return base64.b64encode(data).decode()
    except Exception:
        pass
    return ""

def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    if not bin_str:
        return
    page_bg_img = f'''
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    .stApp > header {{
        background-color: transparent !important;
    }}
    .block-container {{
        background-color: rgba(10, 10, 25, 0.85);
        border-radius: 15px;
        padding: 1rem 2rem;
        box-shadow: 0 0 20px rgba(0, 200, 255, 0.2);
        max-width: 95%;
    }}
    h1, h2, h3, .stMarkdown, .stMetricLabel {{
        color: #e0e0ff !important;
        text-shadow: 0 0 5px rgba(0, 200, 255, 0.5);
    }}
    .stMetricValue {{
        color: #00ffff !important;
        text-shadow: 0 0 10px rgba(0, 255, 255, 0.8);
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

try:
    set_png_as_page_bg('background.png')
except:
    pass

# Helper to provide data
def get_data(endpoint, **kwargs):
    if endpoint == "kpi_total_success_rate":
        rate = df['Success_Flag'].mean() if not df.empty else 0
        return {"success_rate": rate}
    elif endpoint == "growth_trend":
        return get_growth_trend(df)
    elif endpoint == "success_rates":
        return get_success_rates(df)
    elif endpoint == "strategic_focus":
        return get_strategic_focus(df)
    elif endpoint == "orbit_complexity":
        return get_orbit_complexity(df)
    elif endpoint == "model_performance":
        return model_metrics
    elif endpoint == "feature_importance":
        return get_feature_importance(pipeline=model_obj)
    elif endpoint == "predict_mission":
        if model_obj is None:
            return {"prediction_probability": None}
        prob = predict_success(kwargs.get('vehicle'), kwargs.get('orbit'), pipeline=model_obj)
        return {"prediction_probability": prob}
    return None

# Sidebar
st.sidebar.title("ISRO Analytics")
st.sidebar.info("Analyze historical mission data and predict future outcomes.")

# Header
st.title("🚀 ISRO Mission Success Probability Estimator (Exploratory Analysis)")
st.markdown("Estimates mission success probability based on historical patterns; not intended for operational forecasting.")

# KPI Section
kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
with kpi_col1:
    kpi_data = get_data("kpi_total_success_rate")
    if kpi_data:
        rate = kpi_data.get("success_rate", 0) * 100
        st.metric(label="Overall Mission Success Rate", value=f"{rate:.1f}%")

# Main Tabs
tab1, tab2 = st.tabs(["📈 Strategic Trends", "🔮 Prediction Tool"])

with tab1:
    st.header("Strategic Portfolio Analysis")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Growth Trend")
        growth_data = get_data("growth_trend")
        if growth_data:
            df_growth = pd.DataFrame(growth_data)
            fig_growth = px.line(df_growth, x='Year', y='Mission_Count', title='Missions Launched per Year', markers=True)
            fig_growth.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e0e0ff')
            st.plotly_chart(fig_growth, use_container_width=True)
    with col2:
        st.subheader("Success Rates by Vehicle Family")
        success_data = get_data("success_rates")
        if success_data:
            df_success = pd.DataFrame(success_data)
            fig_success = px.bar(df_success, x='Family', y='Success_Rate', title='Success Rate (Top Families)', 
                                 text_auto='.2%', color='Family')
            fig_success.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e0e0ff')
            st.plotly_chart(fig_success, use_container_width=True)
    
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Strategic Focus (Application)")
        focus_data = get_data("strategic_focus")
        if focus_data:
            df_focus = pd.DataFrame(focus_data)
            fig_focus = px.pie(df_focus, names='Application', values='Count', title='Mission Distribution by Application')
            fig_focus.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#e0e0ff')
            st.plotly_chart(fig_focus, use_container_width=True)
    with col4:
        st.subheader("Mission Capabilities (Vehicle to Orbit)")
        orbit_data = get_data("orbit_complexity")
        if orbit_data:
            df_links = pd.DataFrame(orbit_data)
            fig_bar = px.bar(df_links, x='source', y='value', color='target', 
                             title="Launch Vehicle Capabilities",
                             labels={'source': 'Launch Vehicle', 'value': 'Number of Missions', 'target': 'Orbit Type'},
                             text_auto=True)
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e0e0ff')
            st.plotly_chart(fig_bar, use_container_width=True)

with tab2:
    st.header("Exploratory Success Estimation")
    perf_data = get_data("model_performance")
    if perf_data:
        st.subheader("Model Performance Indicators")
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric("Accuracy", f"{perf_data.get('Accuracy',0):.2f}")
        m_col2.metric("Precision", f"{perf_data.get('Precision',0):.2f}")
        m_col3.metric("Recall", f"{perf_data.get('Recall',0):.2f}")
        m_col4.metric("F1-Score", f"{perf_data.get('F1-Score',0):.2f}")
    
    feat_data = get_data("feature_importance")
    if feat_data:
        st.subheader("Top Influential Features")
        df_feat = pd.DataFrame(feat_data)
        fig_feat = px.bar(df_feat, y='Feature', x='Importance', orientation='h', color='Importance')
        fig_feat.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e0e0ff')
        st.plotly_chart(fig_feat, use_container_width=True)
    
    with st.expander("⚠️ Model Limitations & Disclaimer"):
        st.markdown(r"""
        - **Data Source**: This model is trained on historical ISRO mission data from Kaggle (1963-2025).
        - **Class Imbalance**: High metrics are influenced by the high historical success rate $(\sim93\%)$.
        """, unsafe_allow_html=True)
    
    st.divider()
    with st.form("prediction_form"):
        vehicle_options = sorted(df['launch_vehicle'].unique().tolist()) if not df.empty else ['PSLV']
        orbit_options = sorted(df['orbit_type'].unique().tolist()) if not df.empty else ['LEO']
        p_vehicle = st.selectbox("Launch Vehicle", vehicle_options)
        p_orbit = st.selectbox("Orbit", orbit_options)
        if st.form_submit_button("Predict Probability"):
            res = get_data("predict_mission", vehicle=p_vehicle, orbit=p_orbit)
            prob = res.get("prediction_probability")
            if prob is not None:
                st.success(f"Estimated Success Probability: {float(prob)*100:.2f}%")
                if float(prob) > 0.8: st.balloons()
            else:
                st.error("Prediction unavailable.")
