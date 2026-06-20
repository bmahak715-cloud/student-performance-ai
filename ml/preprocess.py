import os
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

from ml.feature_engineering import engineer_features_df

# Define list of features used as inputs to the model
FEATURE_COLUMNS = [
    'attendance_percentage',
    'assignment_average',
    'quiz_average',
    'midterm_marks',
    'practical_marks',
    'project_marks',
    'previous_gpa',
    'login_frequency',
    'materials_accessed',
    'quiz_attempts',
    'assignments_submitted',
    'total_assignments',
    'late_submissions',
    'consecutive_absences',
    'discussion_participation',
    'time_spent',
    
    # Engineered features
    'assignment_submission_rate',
    'late_submission_rate',
    'lms_engagement_score',
    'avg_assessment_score',
    'high_consecutive_absences',
    'gpa_performance_gap',
    'materials_per_login'
]

def load_and_prepare_data(csv_path="datasets/student_data.csv"):
    """
    Load dataset, handle basic cleaning, and execute feature engineering.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found at {csv_path}. Please run generate_dataset.py first.")
        
    df = pd.read_csv(csv_path)
    
    # Basic data cleaning: drop duplicates
    df = df.drop_duplicates()
    
    # Feature Engineering
    df = engineer_features_df(df)
    
    return df

def build_preprocessing_pipeline():
    """
    Build a scikit-learn preprocessing pipeline for numerical features.
    """
    # Numerical pipeline: impute missing values with median, then standardize
    num_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', num_pipeline, FEATURE_COLUMNS)
        ],
        remainder='drop'  # Drop any other columns (e.g. student_id, final_marks, at_risk)
    )
    
    return preprocessor

def get_train_test_data(csv_path="datasets/student_data.csv", test_size=0.2, random_state=42):
    """
    Prepares features and targets, splits into train/test sets, 
    fits the preprocessor, and returns ready-to-train datasets and pipeline.
    """
    df = load_and_prepare_data(csv_path)
    
    # Separate features and targets
    X = df[FEATURE_COLUMNS]
    y_reg = df['final_marks']
    y_clf = df['at_risk']
    
    # Train-test split
    # We do a stratified split on risk class to keep distribution consistent
    X_train, X_test, y_train_reg, y_test_reg, y_train_clf, y_test_clf = train_test_split(
        X, y_reg, y_clf,
        test_size=test_size,
        random_state=random_state,
        stratify=y_clf
    )
    
    # Create and fit preprocessing pipeline
    preprocessor = build_preprocessing_pipeline()
    X_train_processed = preprocessor.fit_transform(X_train)
    X_test_processed = preprocessor.transform(X_test)
    
    # Save the pipeline and feature list to models directory
    os.makedirs("models", exist_ok=True)
    joblib.dump(preprocessor, "models/preprocessing_pipeline.pkl")
    joblib.dump(FEATURE_COLUMNS, "models/feature_names.pkl")
    print("Preprocessing pipeline and feature names successfully saved.")
    
    return {
        'X_train': X_train,
        'X_test': X_test,
        'X_train_proc': X_train_processed,
        'X_test_proc': X_test_processed,
        'y_train_reg': y_train_reg,
        'y_test_reg': y_test_reg,
        'y_train_clf': y_train_clf,
        'y_test_clf': y_test_clf,
        'preprocessor': preprocessor
    }

if __name__ == '__main__':
    get_train_test_data()
