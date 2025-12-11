import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Configuration
API_URL = "http://localhost:8000/api"

st.set_page_config(
    page_title="ISRO Mission Analyzer",
    page_icon="🚀",
    layout="wide"
)

def fetch_data(endpoint):
    try:
        response = requests.get(f"{API_URL}/{endpoint}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching data from {endpoint}: {response.status_code}")
            return []
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to Backend API. Please ensure FastAPI is running.")
        return []

# Sidebar
st.sidebar.title("ISRO Analytics")
st.sidebar.info("Analyze historical mission data and predict future outcomes.")

# Header
st.title("🚀 ISRO Mission Analyzer & Success Predictor")
st.markdown("Deep dive into the strategic evolution of Indian Space Research Organisation.")

# KPI Section
kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
with kpi_col1:
    kpi_data = fetch_data("kpi_total_success_rate")
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
        growth_data = fetch_data("growth_trend")
        if growth_data:
            df_growth = pd.DataFrame(growth_data)
            fig_growth = px.line(df_growth, x='Year', y='Mission_Count', title='Missions Launched per Year', markers=True)
            st.plotly_chart(fig_growth, use_container_width=True)
            
    with col2:
        st.subheader("Success Rates by Vehicle Family")
        success_data = fetch_data("success_rates")
        if success_data:
            df_success = pd.DataFrame(success_data)
            fig_success = px.bar(df_success, x='Family', y='Success_Rate', title='Success Rate (Top Families)', 
                                 text_auto='.2%', color='Family')
            st.plotly_chart(fig_success, use_container_width=True)
            
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Strategic Focus (Application)")
        focus_data = fetch_data("strategic_focus")
        if focus_data:
            df_focus = pd.DataFrame(focus_data)
            fig_focus = px.pie(df_focus, names='Application', values='Count', title='Mission Distribution by Application')
            st.plotly_chart(fig_focus, use_container_width=True)
            
    with col4:
        st.subheader("Orbit Complexity Matrix")
        orbit_data = fetch_data("orbit_complexity")
        if orbit_data:
            # Data comes as record list, need to reshape for heatmap
            df_orbit = pd.DataFrame(orbit_data)
            # The API returns records with Family and columns for each Orbit. Melt it.
            df_orbit = df_orbit.set_index('Family')
            fig_matrix = px.imshow(df_orbit, title='Vehicle vs Orbit Type (Normalized)', text_auto=True, aspect="auto")
            st.plotly_chart(fig_matrix, use_container_width=True)

with tab2:
    st.header("Mission Success Predictor")
    st.markdown("Predict the probability of success for a hypothetical mission based on historical patterns.")
    
    # Model Performance
    perf_data = fetch_data("model_performance")
    if perf_data:
        st.write("Current Model Performance (Test Set):")
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric("Accuracy", f"{perf_data.get('Accuracy',0):.2f}")
        m_col2.metric("Precision", f"{perf_data.get('Precision',0):.2f}")
        m_col3.metric("Recall", f"{perf_data.get('Recall',0):.2f}")
        m_col4.metric("F1-Score", f"{perf_data.get('F1-Score',0):.2f}")
    
    st.divider()
    
    # Input Form
    with st.form("prediction_form"):
        # We need options for selectbox. Hardcoding major ones or fetching unique values would be best.
        # For simplicity, hardcoding common ones found in dataset.
        vehicle_options = ['PSLV', 'GSLV', 'LVM3', 'SSLV', 'ASLV', 'SLV-3']
        orbit_options = ['SSPO', 'GSO', 'GTO', 'LEO', 'Lunar', 'Suborbital', 'Martian']
        
        p_vehicle = st.selectbox("Launch Vehicle Family/Type", vehicle_options)
        p_orbit = st.selectbox("Target Orbit", orbit_options)
        
        submit = st.form_submit_button("Predict Probability")
        
        if submit:
            payload = {"vehicle": p_vehicle, "orbit": p_orbit}
            try:
                res = requests.post(f"{API_URL}/predict_mission", json=payload)
                if res.status_code == 200:
                    prob = res.json().get("prediction_probability", 0)
                    st.success(f"Predicted Success Probability: {prob*100:.2f}%")
                    if prob > 0.8:
                        st.balloons()
                else:
                    st.error("Prediction failed.")
            except Exception as e:
                st.error(f"Error: {e}")
