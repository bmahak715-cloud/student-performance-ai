import numpy as np
import joblib
from config import Config

def explain_prediction(student_features, prediction_results):
    """
    Explain a specific prediction by identifying which metrics contributed 
    most to increasing or reducing the academic risk.
    Uses model feature importances combined with student feature deviations from typical means.
    """
    # Load feature names and risk model
    try:
        risk_model = joblib.load(Config.RISK_MODEL_PATH)
        feature_names = joblib.load(Config.FEATURE_NAMES_PATH)
        preprocessor = joblib.load(Config.PREPROCESSOR_PATH)
    except Exception:
        # Fallback if models are not loaded
        return {
            'risk_increasing_factors': ["Unavailable model assets"],
            'risk_reducing_factors': [],
            'attribution': {}
        }
        
    engineered_dict = prediction_results['engineered_features']
    processed_array = prediction_results['processed_features'] # Standardized values
    
    # Extract feature importances or coefficients
    importances = None
    if hasattr(risk_model, 'feature_importances_'):
        importances = risk_model.feature_importances_
    elif hasattr(risk_model, 'coef_'):
        importances = np.abs(risk_model.coef_[0])
    else:
        # Fallback: uniform importances
        importances = np.ones(len(feature_names)) / len(feature_names)
        
    # Scale importances to sum to 100 for readability
    importances = (importances / np.sum(importances)) * 100
    
    # Define directional impact:
    # A positive processed value (above mean) for a "good" feature reduces risk.
    # A negative processed value (below mean) for a "good" feature increases risk.
    # For "bad" features (late submission rate, consecutive absences, late arrivals, gap):
    # A positive processed value (above mean) increases risk, negative reduces risk.
    
    negative_impact_features = {
        'late_submissions', 'late_submission_rate', 'consecutive_absences', 
        'high_consecutive_absences', 'late_arrivals'
    }
    
    attributions = {}
    for i, name in enumerate(feature_names):
        std_val = processed_array[i] # standard deviations from mean
        importance = importances[i]
        
        # Calculate individual contribution score
        # For bad features, a positive std_val increases risk.
        if name in negative_impact_features:
            impact = std_val * importance
        else:
            # For good features, a negative std_val (below average) increases risk
            impact = -std_val * importance
            
        attributions[name] = float(np.round(impact, 2))
        
    # Map feature names to user-friendly plain English descriptions
    feature_labels = {
        'attendance_percentage': 'Attendance rate',
        'assignment_average': 'Assignment average marks',
        'quiz_average': 'Quiz average marks',
        'midterm_marks': 'Midterm exam marks',
        'practical_marks': 'Practical lab marks',
        'project_marks': 'Project marks',
        'previous_gpa': 'Prior cumulative GPA',
        'login_frequency': 'LMS login frequency',
        'materials_accessed': 'LMS materials accessed',
        'quiz_attempts': 'LMS quiz practice attempts',
        'assignments_submitted': 'LMS assignments submitted',
        'total_assignments': 'Total course assignments',
        'late_submissions': 'Number of late submissions',
        'consecutive_absences': 'Consecutive days absent',
        'discussion_participation': 'LMS discussion board activity',
        'time_spent': 'LMS platform study time',
        'assignment_submission_rate': 'Assignment completion rate',
        'late_submission_rate': 'Late submission rate',
        'lms_engagement_score': 'LMS engagement score',
        'avg_assessment_score': 'Average assessment marks',
        'high_consecutive_absences': 'High consecutive absence warning',
        'gpa_performance_gap': 'Gap between previous GPA and current scores',
        'materials_per_login': 'LMS download density per login'
    }
    
    # Sort features by attribution impact
    sorted_features = sorted(attributions.items(), key=lambda x: x[1], reverse=True)
    
    increasing = []
    reducing = []
    
    # Group into contributors
    for name, score in sorted_features:
        label = feature_labels.get(name, name)
        val = engineered_dict.get(name, 0)
        
        if score > 0.8: # Feature contributed to higher risk
            if name == 'attendance_percentage' and val < 75:
                increasing.append(f"Low attendance rate ({val:.1f}%)")
            elif name == 'assignment_submission_rate' and val < 0.8:
                increasing.append(f"Low assignment submission rate ({val*100:.1f}%)")
            elif name == 'consecutive_absences' and val >= 3:
                increasing.append(f"Frequent consecutive absences ({val} days)")
            elif name == 'avg_assessment_score' and val < 50:
                increasing.append(f"Poor average internal marks ({val:.1f}/100)")
            elif name == 'midterm_marks' and val < 50:
                increasing.append(f"Underperformance in midterm exam ({val:.1f}/100)")
            elif name == 'late_submission_rate' and val > 0.2:
                increasing.append(f"High frequency of late submissions ({val*100:.1f}%)")
            elif name == 'lms_engagement_score' and val < 40:
                increasing.append(f"Low engagement score on the LMS ({val:.1f}/100)")
            else:
                # General descriptive fallback
                increasing.append(f"Below average values in: {label}")
                
        elif score < -0.8: # Feature contributed to lower risk
            if name == 'attendance_percentage' and val >= 85:
                reducing.append(f"Consistent class attendance ({val:.1f}%)")
            elif name == 'assignment_submission_rate' and val >= 0.95:
                reducing.append(f"Excellent assignment completion rate ({val*100:.1f}%)")
            elif name == 'avg_assessment_score' and val >= 75:
                reducing.append(f"Strong performance in internal assessments ({val:.1f}/100)")
            elif name == 'project_marks' and val >= 75:
                reducing.append(f"High scores in practical project work ({val:.1f}/100)")
            elif name == 'previous_gpa' and val >= 3.2:
                reducing.append(f"Strong prior academic foundation (GPA: {val:.2f})")
            elif name == 'lms_engagement_score' and val >= 70:
                reducing.append(f"High digital engagement with course LMS ({val:.1f}/100)")
            else:
                reducing.append(f"Positive engagement in: {label}")

    # Remove duplicates and cap at top 4 for concise display
    increasing = list(dict.fromkeys(increasing))[:4]
    reducing = list(dict.fromkeys(reducing))[:4]
    
    # Fallback default factors if none met criteria
    if not increasing:
        increasing = ["None detected (Normal performance metrics)"]
    if not reducing:
        reducing = ["General average performance across modules"]
        
    return {
        'risk_increasing_factors': increasing,
        'risk_reducing_factors': reducing,
        'attributions': attributions
    }
