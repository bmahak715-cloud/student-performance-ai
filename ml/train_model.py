import os
import json
import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingRegressor, GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier

from ml.preprocess import get_train_test_data, FEATURE_COLUMNS
from ml.evaluate_model import evaluate_regression, evaluate_classification, evaluate_fairness

def train_all_models(csv_path="datasets/student_data.csv"):
    """
    Train and evaluate multiple models, selecting the best ones to persist.
    """
    print("--- STEP 1: Loading Preprocessed Train/Test Datasets ---")
    data = get_train_test_data(csv_path)
    
    X_train_proc = data['X_train_proc']
    X_test_proc = data['X_test_proc']
    y_train_reg = data['y_train_reg']
    y_test_reg = data['y_test_reg']
    y_train_clf = data['y_train_clf']
    y_test_clf = data['y_test_clf']
    preprocessor = data['preprocessor']
    
    print("\n--- STEP 2: Training Regression Models (Final Marks Prediction) ---")
    reg_models = {
        'Linear Regression': LinearRegression(),
        'Random Forest Regressor': RandomForestRegressor(n_estimators=100, random_state=42),
        'Gradient Boosting Regressor': GradientBoostingRegressor(n_estimators=100, random_state=42)
    }
    
    best_reg_name = None
    best_reg_r2 = -float('inf')
    best_reg_model = None
    reg_results = {}
    
    for name, model in reg_models.items():
        print(f"Training {name}...")
        model.fit(X_train_proc, y_train_reg)
        metrics = evaluate_regression(model, X_test_proc, y_test_reg)
        reg_results[name] = metrics
        print(f"  Evaluation -> MAE: {metrics['mae']:.3f}, RMSE: {metrics['rmse']:.3f}, R2: {metrics['r2']:.3f}")
        
        # Select best model based on R2 score
        if metrics['r2'] > best_reg_r2:
            best_reg_r2 = metrics['r2']
            best_reg_name = name
            best_reg_model = model
            
    print(f"\n>> Best Regression Model Selected: {best_reg_name} (R2: {best_reg_r2:.3f})")
    
    print("\n--- STEP 3: Training Classification Models (Academic Risk Prediction) ---")
    clf_models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'Decision Tree Classifier': DecisionTreeClassifier(max_depth=5, random_state=42),
        'Random Forest Classifier': RandomForestClassifier(n_estimators=100, random_state=42),
        'Gradient Boosting Classifier': GradientBoostingClassifier(n_estimators=100, random_state=42)
    }
    
    best_clf_name = None
    best_clf_f1 = -float('inf')
    best_clf_model = None
    clf_results = {}
    
    for name, model in clf_models.items():
        print(f"Training {name}...")
        model.fit(X_train_proc, y_train_clf)
        metrics = evaluate_classification(model, X_test_proc, y_test_clf)
        clf_results[name] = metrics
        print(f"  Evaluation -> Accuracy: {metrics['accuracy']:.3f}, Precision: {metrics['precision']:.3f}, Recall: {metrics['recall']:.3f}, F1: {metrics['f1']:.3f}")
        
        # Select best model based on F1-Score (balances precision and recall)
        # We also prioritize Recall in case of a tie
        if metrics['f1'] > best_clf_f1:
            best_clf_f1 = metrics['f1']
            best_clf_name = name
            best_clf_model = model
            
    print(f"\n>> Best Classification Model Selected: {best_clf_name} (F1-score: {best_clf_f1:.3f}, Recall: {clf_results[best_clf_name]['recall']:.3f})")
    
    # Save the best models to the models directory
    os.makedirs("models", exist_ok=True)
    joblib.dump(best_reg_model, "models/marks_model.pkl")
    joblib.dump(best_clf_model, "models/risk_model.pkl")
    print("\nSuccessfully saved best model checkpoints to models/ directory.")
    
    print("\n--- STEP 4: Auditing Subgroup Fairness ---")
    # Load raw dataframe for fairness assessment
    raw_df = pd.read_csv(csv_path)
    # Apply feature engineering so engineered columns exist in the dataframe
    from ml.feature_engineering import engineer_features_df
    raw_df_engineered = engineer_features_df(raw_df)
    fairness_metrics = evaluate_fairness(raw_df_engineered, best_clf_model, preprocessor, FEATURE_COLUMNS)
    
    # Structure evaluation meta report
    report = {
        'model_metadata': {
            'best_regression_model': best_reg_name,
            'best_classification_model': best_clf_name,
            'model_version': '1.0.0'
        },
        'regression_metrics': reg_results,
        'classification_metrics': clf_results,
        'fairness_audit': fairness_metrics
    }
    
    with open("models/evaluation_results.json", "w") as f:
        json.dump(report, f, indent=4)
    print("Saved comprehensive evaluation results report to models/evaluation_results.json")
    
    return report

if __name__ == '__main__':
    train_all_models()
