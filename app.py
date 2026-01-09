import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
import os
import sys

# Ensure backend is in path
sys.path.append(os.path.dirname(__file__))

# Import backend modules directly for Streamlit Cloud deployment
from backend.data_loader import load_data
from backend.eda import get_growth_trend, get_success_rates, get_strategic_focus, get_orbit_complexity
from backend.ml_model import train_model, get_model_metrics, predict_success, get_feature_importance

# Configuration
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api")

st.set_page_config(
    page_title="ISRO Mission Analyzer",
    page_icon="🚀",
    layout="wide"
)

# --- Data & Model Initialization (Streamlit Native) ---
@st.cache_resource
def init_app_state():
    df = load_data()
    if not df.empty:
        train_model(df)
    return df

# Initialize
df = init_app_state()

# --- Custom CSS for Space Theme ---
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
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
    /* Make containers semi-transparent to see background */
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
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {{
        width: 250px;
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
except Exception as e:
    pass

# Helper to provide data either from API or Local Functions
def get_data(endpoint, **kwargs):
    # If API_URL is set to a non-local or explicitly configured, try requests
    # But for a simpler "whole-in-streamlit" deployment, we prefer local calls.
    # We will use local calls as primary to ensure Streamlit Cloud works without backend setup.
    
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
        return get_model_metrics()
    elif endpoint == "feature_importance":
        return get_feature_importance()
    elif endpoint == "predict_mission":
        prob = predict_success(kwargs.get('vehicle'), kwargs.get('orbit'))
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
    st.markdown("Estimate the probability of success for a hypothetical mission configuration based on historical patterns.")
    
    # Model Performance
    perf_data = get_data("model_performance")
    if perf_data:
        st.subheader("Model Performance Indicators")
        st.info("“High recall and accuracy are influenced by the dominance of successful missions in historical data.”")
        
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric("Accuracy", f"{perf_data.get('Accuracy',0):.2f}")
        m_col2.metric("Precision", f"{perf_data.get('Precision',0):.2f}")
        m_col3.metric("Recall", f"{perf_data.get('Recall',0):.2f}")
        m_col4.metric("F1-Score", f"{perf_data.get('F1-Score',0):.2f}")
        
        st.caption("“ROC-AUC is de-emphasized due to class imbalance in historical mission outcomes; precision–recall metrics better reflect model behavior.”")
    
    # Feature Importance Chart
    feat_data = get_data("feature_importance")
    if feat_data:
        st.subheader("Top Influential Features (Tree-Based Importance)")
        df_feat = pd.DataFrame(feat_data)
        fig_feat = px.bar(df_feat, y='Feature', x='Importance', orientation='h', 
                          title='Top 10 Influential Factors (Exploratory)',
                          color='Importance', color_continuous_scale='Viridis')
        fig_feat.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e0e0ff',
                               yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_feat, use_container_width=True)
    
    # Model Limitations
    with st.expander("⚠️ Model Limitations & Disclaimer"):
        st.markdown("""
        - **Data Source**: This model is trained on historical ISRO mission data from Kaggle (1963-2025).
        - **Exclusions**: Real-time factors like weather, sensor health, and payload-specific complexities are not captured.
        - **Interpretations**: Predictions are probabilistic estimates based on historical trends for exploratory analysis, not for operational mission guarantees.
        - **Class Imbalance**: High metrics are influenced by the high historical success rate $(\sim93\%)$.
        """)
    
    st.divider()
    
    # Input Form
    with st.form("prediction_form"):
        vehicle_options = sorted(df['launch_vehicle'].unique().tolist()) if not df.empty else ['PSLV', 'GSLV']
        orbit_options = sorted(df['orbit_type'].unique().tolist()) if not df.empty else ['SSPO', 'GSO']
        
        p_vehicle = st.selectbox("Launch Vehicle Family/Type", vehicle_options)
        p_orbit = st.selectbox("Target Orbit", orbit_options)
        
        submit = st.form_submit_button("Predict Probability")
        
        if submit:
            res = get_data("predict_mission", vehicle=p_vehicle, orbit=p_orbit)
            if res:
                prob = res.get("prediction_probability", 0)
                st.success(f"Estimated Success Probability: {prob*100:.2f}%")
                if prob > 0.8:
                    st.balloons()
            else:
                st.error("Prediction failed.")
