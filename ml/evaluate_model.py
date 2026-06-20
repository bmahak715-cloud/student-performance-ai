import numpy as np
import pandas as pd
from sklearn.metrics import (
    mean_absolute_error, 
    mean_squared_error, 
    r2_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix
)

def evaluate_regression(model, X_proc, y_true):
    """
    Evaluate regression model performance.
    """
    y_pred = model.predict(X_proc)
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_true, y_pred)
    
    return {
        'mae': float(mae),
        'rmse': float(rmse),
        'r2': float(r2)
    }

def evaluate_classification(model, X_proc, y_true):
    """
    Evaluate classification model performance.
    """
    y_pred = model.predict(X_proc)
    
    # Check if model has predict_proba
    if hasattr(model, "predict_proba"):
        y_prob = model.predict_proba(X_proc)[:, 1]
        auc = roc_auc_score(y_true, y_prob)
    else:
        y_prob = None
        auc = 0.0
        
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    cm = confusion_matrix(y_true, y_pred).tolist()
    
    return {
        'accuracy': float(acc),
        'precision': float(prec),
        'recall': float(rec),
        'f1': float(f1),
        'auc': float(auc),
        'confusion_matrix': cm
    }

def evaluate_fairness(df, risk_model, preprocessor, feature_names):
    """
    Assess prediction fairness across subgroups.
    For demonstration in Responsible AI guidelines:
    We group students by simulated background attributes (e.g. course types or age brackets).
    This computes accuracy, precision, and recall by group to audit potential bias.
    """
    results = {}
    
    # Create copy and generate predictions
    df_eval = df.copy()
    X_features = df_eval[feature_names]
    X_proc = preprocessor.transform(X_features)
    
    df_eval['pred_risk'] = risk_model.predict(X_proc)
    
    # 1. Audit by Semester (Lower vs Upper Semesters)
    df_eval['semester_group'] = np.where(df_eval['student_id'].apply(lambda x: hash(x) % 2 == 0), 'Sem Group A', 'Sem Group B')
    
    # 2. Audit by Age (Under 21 vs 21 and Over)
    # We will simulate age for fairness audit if not directly used in features
    np.random.seed(42)
    df_eval['audit_age_group'] = np.where(np.random.randint(18, 24, len(df_eval)) < 21, 'Under 21', '21 and Over')
    
    for group_col in ['semester_group', 'audit_age_group']:
        results[group_col] = {}
        for val in df_eval[group_col].unique():
            sub_df = df_eval[df_eval[group_col] == val]
            
            if len(sub_df) == 0:
                continue
                
            y_true = sub_df['at_risk']
            y_pred = sub_df['pred_risk']
            
            acc = accuracy_score(y_true, y_pred)
            rec = recall_score(y_true, y_pred, zero_division=0)
            prec = precision_score(y_true, y_pred, zero_division=0)
            
            # FPR and FNR
            tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
            fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
            fnr = fn / (fn + tp) if (fn + tp) > 0 else 0
            
            results[group_col][val] = {
                'sample_size': int(len(sub_df)),
                'accuracy': float(acc),
                'precision': float(prec),
                'recall': float(rec),
                'fpr': float(fpr),
                'fnr': float(fnr)
            }
            
    return results
