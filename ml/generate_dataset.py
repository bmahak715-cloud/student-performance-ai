import os
import pandas as pd
import numpy as np

def generate_student_dataset(n_records=550, output_path="datasets/student_data.csv"):
    """
    Generate realistic synthetic student dataset for performance prediction.
    Correlations:
    - High attendance -> higher marks, lower risk
    - High assignment/quiz/midterm -> higher final marks, lower risk
    - High previous GPA -> higher final marks, lower risk
    - Higher LMS usage -> higher marks, lower risk
    - Adds random noise to simulate real-world variability.
    """
    np.random.seed(42)
    
    # 1. Generate core independent metrics
    student_ids = [f"STU{2000 + i}" for i in range(n_records)]
    
    previous_gpa = np.random.uniform(2.0, 4.0, n_records)
    attendance_percentage = np.random.beta(a=7, b=2, size=n_records) * 100  # Skewed towards high attendance
    
    # Academic internal marks (correlated with previous_gpa and attendance)
    # Start with base score influenced by GPA
    base_academic_ability = (previous_gpa - 2.0) / 2.0  # Scale 0.0 to 1.0
    
    assignment_average = np.clip(
        base_academic_ability * 40 + (attendance_percentage / 100) * 40 + np.random.normal(15, 8, n_records), 
        0, 100
    )
    quiz_average = np.clip(
        base_academic_ability * 35 + (attendance_percentage / 100) * 35 + np.random.normal(20, 10, n_records), 
        0, 100
    )
    midterm_marks = np.clip(
        base_academic_ability * 45 + (attendance_percentage / 100) * 30 + np.random.normal(18, 10, n_records), 
        0, 100
    )
    practical_marks = np.clip(
        base_academic_ability * 30 + np.random.normal(50, 15, n_records), 
        0, 100
    )
    project_marks = np.clip(
        base_academic_ability * 40 + (attendance_percentage / 100) * 35 + np.random.normal(20, 10, n_records), 
        0, 100
    )
    
    # LMS Engagement features
    total_assignments = np.random.randint(8, 15, n_records)
    
    # Submission rate correlated with academic ability and attendance
    sub_ratio = np.clip(
        (attendance_percentage / 100) * 0.7 + base_academic_ability * 0.2 + np.random.uniform(0, 0.15, n_records), 
        0, 1
    )
    assignments_submitted = np.round(sub_ratio * total_assignments).astype(int)
    
    # Prevent negative submissions and handle boundary cases
    assignments_submitted = np.clip(assignments_submitted, 0, total_assignments)
    
    # Late submissions (higher for low attendance/academic ability)
    late_submissions = np.zeros(n_records, dtype=int)
    for i in range(n_records):
        if assignments_submitted[i] > 0:
            late_prob = 0.4 - 0.2 * base_academic_ability[i] - 0.1 * (attendance_percentage[i]/100)
            late_prob = max(0.05, min(0.7, late_prob))
            late_submissions[i] = np.random.binomial(assignments_submitted[i], late_prob)
        else:
            late_submissions[i] = 0
            
    consecutive_absences = np.zeros(n_records, dtype=int)
    for i in range(n_records):
        att = attendance_percentage[i]
        if att < 60:
            consecutive_absences[i] = np.random.randint(4, 12)
        elif att < 75:
            consecutive_absences[i] = np.random.randint(2, 6)
        elif att < 90:
            consecutive_absences[i] = np.random.randint(0, 3)
        else:
            consecutive_absences[i] = np.random.randint(0, 2)
            
    login_frequency = np.clip(
        np.round((attendance_percentage / 10) + base_academic_ability * 5 + np.random.normal(3, 2, n_records)), 
        1, 30
    ).astype(int)
    
    materials_accessed = np.clip(
        np.round(login_frequency * 2.5 + np.random.normal(5, 5, n_records)), 
        0, 100
    ).astype(int)
    
    quiz_attempts = np.clip(
        np.round(quiz_average / 15 + np.random.normal(1, 1, n_records)), 
        0, 10
    ).astype(int)
    
    discussion_participation = np.zeros(n_records, dtype=int)
    for i in range(n_records):
        disc_prob = base_academic_ability[i] * 0.6 + 0.2
        discussion_participation[i] = np.random.poisson(disc_prob * 4)
        
    time_spent = np.clip(
        login_frequency * 0.8 + materials_accessed * 0.1 + np.random.normal(5, 3, n_records), 
        1.0, 60.0
    )
    
    # 2. Generate target final marks
    # Logic: Weighted sum of assessment indicators + attendance penalization + randomness
    assessment_part = (
        0.25 * assignment_average + 
        0.15 * quiz_average + 
        0.30 * midterm_marks + 
        0.10 * practical_marks + 
        0.20 * project_marks
    )
    
    # Attendance impact
    attendance_penalty = np.zeros(n_records)
    for i in range(n_records):
        if attendance_percentage[i] < 75:
            # Steep penalty below standard 75% requirement
            attendance_penalty[i] = (75 - attendance_percentage[i]) * 0.6
            
    # LMS engagement impact (positive boost for highly engaged, penalty for disengaged)
    lms_submit_rate = assignments_submitted / total_assignments
    lms_score = (lms_submit_rate * 50 + (login_frequency / 30) * 20 + (time_spent / 60) * 20 + (discussion_participation / 15) * 10)
    
    lms_adjustment = (lms_score - 50) * 0.15  # Up to +7.5 or -7.5 marks
    
    final_marks = assessment_part - attendance_penalty + lms_adjustment + np.random.normal(0, 3, n_records)
    final_marks = np.clip(np.round(final_marks, 1), 0, 100)
    
    # 3. Generate risk category (at_risk label)
    # Predictor of failing (final mark < 50) or having critical warning signs (like attendance < 60% or extreme disengagement)
    at_risk = np.zeros(n_records, dtype=int)
    for i in range(n_records):
        risk_score = 0.0
        # Contribution 1: Final performance representation
        risk_score += (100 - final_marks[i]) * 0.5
        # Contribution 2: Attendance issues
        risk_score += (100 - attendance_percentage[i]) * 0.3
        # Contribution 3: Assessment submission deficits
        sub_rate = assignments_submitted[i] / total_assignments[i]
        risk_score += (1.0 - sub_rate) * 25
        # Contribution 4: Low previous GPA
        risk_score += (4.0 - previous_gpa[i]) * 5
        
        # Risk threshold mapping (risk_score ranges roughly 0 to 100)
        # Add random chance to simulate non-linear risk factors
        prob_risk = 1 / (1 + np.exp(-(risk_score - 40) / 6))  # Sigmoid scaling
        at_risk[i] = np.random.choice([0, 1], p=[1 - prob_risk, prob_risk])

    # Ensure dataset directories exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    df = pd.DataFrame({
        'student_id': student_ids,
        'attendance_percentage': np.round(attendance_percentage, 1),
        'assignment_average': np.round(assignment_average, 1),
        'quiz_average': np.round(quiz_average, 1),
        'midterm_marks': np.round(midterm_marks, 1),
        'practical_marks': np.round(practical_marks, 1),
        'project_marks': np.round(project_marks, 1),
        'previous_gpa': np.round(previous_gpa, 2),
        'login_frequency': login_frequency,
        'materials_accessed': materials_accessed,
        'quiz_attempts': quiz_attempts,
        'assignments_submitted': assignments_submitted,
        'total_assignments': total_assignments,
        'late_submissions': late_submissions,
        'consecutive_absences': consecutive_absences,
        'discussion_participation': discussion_participation,
        'time_spent': np.round(time_spent, 1),
        'final_marks': final_marks,
        'at_risk': at_risk
    })
    
    df.to_csv(output_path, index=False)
    print(f"Synthetic dataset of {n_records} records successfully generated and saved to {output_path}")
    print(f"Risk distribution: {df['at_risk'].value_counts(normalize=True).to_dict()}")

if __name__ == '__main__':
    generate_student_dataset()
