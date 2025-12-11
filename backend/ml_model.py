from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import pandas as pd
import numpy as np

# Global variable to store the trained model pipeline
model_pipeline = None
model_metrics = {}

def train_model(df):
    """
    Trains the Random Forest model and stores it globally.
    """
    global model_pipeline, model_metrics
    
    # Feature Selection
    # Features: launch_vehicle (or Family, but let's use raw vehicle for potentially more detail if cardinality isn't crazy, 
    # actually Family might be better for generalization, but the prompt said 'Launch Vehicle' and 'Orbit Type').
    # Let's use 'launch_vehicle' and 'orbit_type' and maybe 'application'.
    # Input JSON for prediction asks for vehicle and orbit.
    
    features = ['launch_vehicle', 'orbit_type']
    target = 'Success_Flag'
    
    X = df[features]
    y = df[target]
    
    # Preprocessing
    categorical_features = ['launch_vehicle', 'orbit_type']
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ]
    )
    
    # Random Forest Pipeline
    clf = Pipeline(steps=[('preprocessor', preprocessor),
                          ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))])
    
    # Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train
    clf.fit(X_train, y_train)
    
    # Evaluate
    y_pred = clf.predict(X_test)
    
    metrics = {
        'Accuracy': accuracy_score(y_test, y_pred),
        'Precision': precision_score(y_test, y_pred, zero_division=0),
        'Recall': recall_score(y_test, y_pred, zero_division=0),
        'F1-Score': f1_score(y_test, y_pred, zero_division=0)
    }
    
    model_pipeline = clf
    model_metrics = metrics
    
    return metrics

def get_model_metrics():
    return model_metrics

def predict_success(vehicle, orbit):
    """
    Predicts probability of success.
    """
    global model_pipeline
    if model_pipeline is None:
        return None
    
    input_data = pd.DataFrame({
        'launch_vehicle': [vehicle],
        'orbit_type': [orbit]
    })
    
    # Predict probability
    # classes_ are usually [0, 1] if both exist.
    # We want probability of class 1.
    probs = model_pipeline.predict_proba(input_data)
    
    # Check if '1' is the second class (index 1) which is standard if 0 and 1 are present.
    # If only one class was in training (e.g. all success), handle that.
    classes = model_pipeline.classes_
    if 1 in classes:
        index_1 = np.where(classes == 1)[0][0]
        return probs[0][index_1]
    else:
        return 0.0 # If model never saw a success? Unlikely for ISRO :)

