import pandas as pd
import numpy as np

def compute_lms_engagement_score(row):
    """
    Calculate an engagement score out of 100 based on LMS activity.
    Formula:
      - Assignment submission rate (weight: 45)
      - Logins relative to class expectation (weight: 20)
      - Hours spent relative to expectation (weight: 20)
      - Discussion participation (weight: 15)
    """
    try:
        total_assign = row.get('total_assignments', 0)
        submitted = row.get('assignments_submitted', 0)
        
        # Submission rate
        sub_rate = submitted / total_assign if total_assign > 0 else 1.0
        
        # Normalize other features (capping at reasonable maximums)
        login_freq = min(row.get('login_frequency', 0), 20) / 20.0
        time_spent = min(row.get('time_spent', 0), 40.0) / 40.0
        disc = min(row.get('discussion_participation', 0), 10) / 10.0
        
        score = (sub_rate * 45) + (login_freq * 20) + (time_spent * 20) + (disc * 15)
        return float(np.round(score, 2))
    except Exception:
        return 50.0 # Return a neutral middle score on error

def engineer_features_df(df):
    """
    Perform feature engineering on a pandas DataFrame.
    """
    df = df.copy()
    
    # 1. Assignment submission rate
    df['assignment_submission_rate'] = np.where(
        df['total_assignments'] > 0, 
        df['assignments_submitted'] / df['total_assignments'], 
        1.0
    )
    
    # 2. Late submission rate
    df['late_submission_rate'] = np.where(
        df['assignments_submitted'] > 0,
        df['late_submissions'] / df['assignments_submitted'],
        0.0
    )
    
    # 3. LMS Engagement score (custom calculated column)
    df['lms_engagement_score'] = df.apply(compute_lms_engagement_score, axis=1)
    
    # 4. Average continuous assessment score (simple average of internal assessments)
    df['avg_assessment_score'] = df[
        ['assignment_average', 'quiz_average', 'midterm_marks', 'practical_marks', 'project_marks']
    ].mean(axis=1)
    
    # 5. Consecutive absence indicator (binary flag for high consecutive absences)
    df['high_consecutive_absences'] = (df['consecutive_absences'] >= 4).astype(int)
    
    # 6. Performance vs Previous GPA gap
    # Map avg_assessment_score (0-100) to GPA scale (0-4) by dividing by 25
    estimated_current_gpa = df['avg_assessment_score'] / 25.0
    df['gpa_performance_gap'] = estimated_current_gpa - df['previous_gpa']
    
    # 7. Engagement consistency (ratio of accessed materials to logins)
    df['materials_per_login'] = np.where(
        df['login_frequency'] > 0,
        df['materials_accessed'] / df['login_frequency'],
        0.0
    )
    
    return df

def engineer_features_single(data):
    """
    Perform feature engineering on a single dictionary representing a student profile.
    Returns a dictionary with both original and engineered features.
    """
    row = data.copy()
    
    # Extract values safely
    tot_assign = float(row.get('total_assignments', 0))
    sub_assign = float(row.get('assignments_submitted', 0))
    late_sub = float(row.get('late_submissions', 0))
    login_freq = float(row.get('login_frequency', 0))
    mat_access = float(row.get('materials_accessed', 0))
    
    # 1. Submission rates
    row['assignment_submission_rate'] = sub_assign / tot_assign if tot_assign > 0 else 1.0
    row['late_submission_rate'] = late_sub / sub_assign if sub_assign > 0 else 0.0
    
    # 2. LMS engagement score
    row['lms_engagement_score'] = compute_lms_engagement_score(row)
    
    # 3. Average assessment marks
    assessments = [
        float(row.get('assignment_average', 0)),
        float(row.get('quiz_average', 0)),
        float(row.get('midterm_marks', 0)),
        float(row.get('practical_marks', 0)),
        float(row.get('project_marks', 0))
    ]
    row['avg_assessment_score'] = sum(assessments) / len(assessments)
    
    # 4. Consecutive absence indicator
    row['high_consecutive_absences'] = 1 if int(row.get('consecutive_absences', 0)) >= 4 else 0
    
    # 5. GPA Performance Gap
    est_gpa = row['avg_assessment_score'] / 25.0
    row['gpa_performance_gap'] = est_gpa - float(row.get('previous_gpa', 0.0))
    
    # 6. Materials per login
    row['materials_per_login'] = mat_access / login_freq if login_freq > 0 else 0.0
    
    return row
