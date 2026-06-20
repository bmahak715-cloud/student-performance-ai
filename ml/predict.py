import os
import joblib
import pandas as pd
import numpy as np

from config import Config
from ml.feature_engineering import engineer_features_single

def load_ml_assets():
    """
    Load saved models and preprocessing pipelines.
    Raises FileNotFoundError if assets are missing.
    """
    if not os.path.exists(Config.PREPROCESSOR_PATH):
        raise FileNotFoundError(f"Preprocessor pipeline not found at {Config.PREPROCESSOR_PATH}. Please train models first.")
    if not os.path.exists(Config.MARKS_MODEL_PATH):
        raise FileNotFoundError(f"Regression model not found at {Config.MARKS_MODEL_PATH}. Please train models first.")
    if not os.path.exists(Config.RISK_MODEL_PATH):
        raise FileNotFoundError(f"Classification model not found at {Config.RISK_MODEL_PATH}. Please train models first.")
    if not os.path.exists(Config.FEATURE_NAMES_PATH):
        raise FileNotFoundError(f"Feature names file not found at {Config.FEATURE_NAMES_PATH}. Please train models first.")
        
    preprocessor = joblib.load(Config.PREPROCESSOR_PATH)
    marks_model = joblib.load(Config.MARKS_MODEL_PATH)
    risk_model = joblib.load(Config.RISK_MODEL_PATH)
    feature_names = joblib.load(Config.FEATURE_NAMES_PATH)
    
    return preprocessor, marks_model, risk_model, feature_names

def predict_student_performance(student_features_dict):
    """
    Generate predictions for a single student profile.
    Inputs:
      - student_features_dict: A dictionary containing academic, attendance, and LMS metrics.
    Outputs:
      - dict containing predicted_marks, risk_probability, risk_level, and engineered_features.
    """
    # 1. Run feature engineering on input
    engineered_dict = engineer_features_single(student_features_dict)
    
    # Load ML assets
    preprocessor, marks_model, risk_model, feature_names = load_ml_assets()
    
    # 2. Build feature DataFrame preserving precise column order
    input_df = pd.DataFrame([engineered_dict])[feature_names]
    
    # 3. Transform inputs using pipeline
    processed_features = preprocessor.transform(input_df)
    
    # 4. Predict Final Marks (Regression)
    predicted_marks = float(marks_model.predict(processed_features)[0])
    predicted_marks = max(0.0, min(100.0, round(predicted_marks, 1)))
    
    # 5. Predict Risk Probability (Classification)
    risk_probability = float(risk_model.predict_proba(processed_features)[0][1])
    
    # 6. Assign risk category based on config thresholds
    if risk_probability < Config.RISK_LOW_THRESHOLD:
        risk_level = 'Low'
    elif risk_probability > Config.RISK_HIGH_THRESHOLD:
        risk_level = 'High'
    else:
        risk_level = 'Medium'
        
    # Calculate simple course completion estimate
    # Completion probability can be inversely related to risk
    completion_probability = max(0.0, min(100.0, (1.0 - risk_probability) * 100))
    completion_probability = round(completion_probability, 1)
    
    return {
        'predicted_marks': predicted_marks,
        'risk_probability': risk_probability,
        'risk_level': risk_level,
        'completion_probability': completion_probability,
        'engineered_features': engineered_dict,
        'processed_features': processed_features[0].tolist(),
        'feature_names': feature_names
    }
