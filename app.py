import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Configuration
import plotly.graph_objects as go
import base64

# Configuration
API_URL = "http://127.0.0.1:8000/api"

st.set_page_config(
    page_title="ISRO Mission Analyzer",
    page_icon="🚀",
    layout="wide"
)

# --- Custom CSS for Space Theme ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
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
        padding: 1rem 2rem; /* Reduced top/bottom padding */
        box-shadow: 0 0 20px rgba(0, 200, 255, 0.2);
        max-width: 95%; /* Make main content wider */
    }}
    /* Sidebar resizing */
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {{
        width: 250px;
    }}
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {{
        width: 250px;
        margin-left: -250px;
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
    st.warning("Background image not found. Using default theme.")

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
            fig_growth.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e0e0ff')
            st.plotly_chart(fig_growth, use_container_width=True)
            
    with col2:
        st.subheader("Success Rates by Vehicle Family")
        success_data = fetch_data("success_rates")
        if success_data:
            df_success = pd.DataFrame(success_data)
            fig_success = px.bar(df_success, x='Family', y='Success_Rate', title='Success Rate (Top Families)', 
                                 text_auto='.2%', color='Family')
            fig_success.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e0e0ff')
            st.plotly_chart(fig_success, use_container_width=True)
            
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Strategic Focus (Application)")
        focus_data = fetch_data("strategic_focus")
        if focus_data:
            df_focus = pd.DataFrame(focus_data)
            fig_focus = px.pie(df_focus, names='Application', values='Count', title='Mission Distribution by Application')
            fig_focus.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#e0e0ff')
            st.plotly_chart(fig_focus, use_container_width=True)
            
    with col4:
        st.subheader("Mission Capabilities (Vehicle to Orbit)")
        orbit_data = fetch_data("orbit_complexity")
        if orbit_data:
            # Data: [{'source': 'PSLV', 'target': 'SSPO', 'value': 20}, ...]
            df_links = pd.DataFrame(orbit_data)
            
            # Simplified Chart: Stacked Bar
            # X = Vehicle (source), Y = Count (value), Color = Orbit (target)
            fig_bar = px.bar(df_links, x='source', y='value', color='target', 
                             title="Launch Vehicle Capabilities",
                             labels={'source': 'Launch Vehicle', 'value': 'Number of Missions', 'target': 'Orbit Type'},
                             text_auto=True)
            
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e0e0ff')
            st.plotly_chart(fig_bar, use_container_width=True)

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
