from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import pandas as pd
from typing import Optional

# Import backend modules
# Since backend is a package, we might need relative imports or ensuring path is correct.
# If running typical python -m backend.main, imports should work.
# Helper for relative imports if run as script or module
try:
    from backend.data_loader import load_data
    from backend.eda import get_growth_trend, get_success_rates, get_strategic_focus, get_orbit_complexity
    from backend.ml_model import train_model, get_model_metrics, predict_success
except ImportError:
    from data_loader import load_data
    from eda import get_growth_trend, get_success_rates, get_strategic_focus, get_orbit_complexity
    from ml_model import train_model, get_model_metrics, predict_success

class MissionInput(BaseModel):
    vehicle: str
    orbit: str

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    global df
    print("Loading data...")
    df = load_data()
    print("Data loaded. Training model...")
    if not df.empty:
        train_model(df)
        print("Model trained.")
    else:
        print("WARNING: Data is empty. Model not trained.")
    yield
    print("Shutting down...")

app = FastAPI(title="ISRO Mission Analyzer API", lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "Welcome to ISRO Mission Analyzer API"}

# EDA Endpoints
@app.get("/api/growth_trend")
def growth_trend():
    return get_growth_trend(df)

@app.get("/api/success_rates")
def success_rates():
    return get_success_rates(df)

@app.get("/api/strategic_focus")
def strategic_focus():
    return get_strategic_focus(df)

@app.get("/api/orbit_complexity")
def orbit_complexity():
    return get_orbit_complexity(df)

# ML Endpoints
@app.get("/api/model_performance")
def model_performance():
    return get_model_metrics()

@app.post("/api/predict_mission")
def predict_mission(mission: MissionInput):
    prob = predict_success(mission.vehicle, mission.orbit)
    if prob is None:
        raise HTTPException(status_code=500, detail="Model not trained or available.")
    return {"prediction_probability": prob}

@app.get("/api/kpi_total_success_rate")
def kpi_total_success_rate():
    # Helper for KPI
    if df.empty: return {"success_rate": 0}
    rate = df['Success_Flag'].mean()
    return {"success_rate": rate}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
