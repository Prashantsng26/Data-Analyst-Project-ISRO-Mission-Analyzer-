# ISRO Mission Analyzer

A full-stack, data-driven web application to analyze the historical success and strategic focus of ISRO missions, and implement a predictive model for mission success.

## Features
- **Data Analysis**: Historical trends of mission launches, success rates by vehicle family, and strategic focus areas.
- **Predictive Modeling**: Random Forest Classifier to predict mission success probability based on Vehicle and Orbit.
- **Interactive Dashboard**: Built with Streamlit for easy visualization.
- **API**: FastAPI backend serving analysis data and prediction model.

## Architecture
- **Backend**: FastAPI (`backend/main.py`)
  - Parses SQL data dump.
  - Cleans and preprocesses data.
  - Exposes REST endpoints for EDA and ML.
- **Frontend**: Streamlit (`app.py`)
  - Consumes backend APIs.
  - Renders Plotly charts and prediction forms.

## How to Run

### Method 1: VS Code (Recommended)
1. Open the **Run and Debug** view in VS Code (Activity Bar on the left).
2. Select **"Run Full Stack App"** from the dropdown at the top.
3. Click the green Play button.
   - This prevents issues with terminal paths and virtual environments as it's pre-configured.

### Method 2: One-Click Script
Open your terminal in the project directory and run:
```bash
./run_app.sh
```

### Method 3: Manual Terminal Commands
If you prefer identifying issues step-by-step, run the backend and frontend in separate terminals:

**Terminal 1 (Backend API):**
```bash
# Activate virtual environment
source venv/bin/activate
# Run FastAPI server
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 (Frontend Dashboard):**
```bash
# Activate virtual environment
source venv/bin/activate
# Run Streamlit
streamlit run app.py
```

## Data
Data is sourced from `isro-missions.sql` which is loaded into an in-memory SQLite database and then processed with Pandas.
