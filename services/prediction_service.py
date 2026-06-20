import json
from datetime import datetime
from utils.database import db, Student, AcademicRecord, Attendance, LMSEngagement, Prediction
from ml.predict import predict_student_performance
from ml.explain import explain_prediction
from services.explanation_service import generate_genai_explanation
from services.intervention_service import suggest_interventions

def get_latest_student_metrics(student_id):
    """
    Fetch the latest student metrics from SQLite and build a flat feature dict.
    Returns None if any core record (Academic, Attendance, LMS) is missing.
    """
    student = Student.query.get(student_id)
    if not student:
        raise ValueError(f"Student with ID {student_id} not found.")
        
    # Get latest records
    academic = AcademicRecord.query.filter_by(student_id=student.id).order_by(AcademicRecord.record_date.desc()).first()
    attendance = Attendance.query.filter_by(student_id=student.id).order_by(Attendance.record_date.desc()).first()
    lms = LMSEngagement.query.filter_by(student_id=student.id).order_by(LMSEngagement.record_date.desc()).first()
    
    # Validation check: require at least one set of records
    if not academic or not attendance or not lms:
        missing = []
        if not academic: missing.append("Academic Records")
        if not attendance: missing.append("Attendance Logs")
        if not lms: missing.append("LMS Engagement Logs")
        raise ValueError(f"Cannot run prediction. Missing: {', '.join(missing)} for student {student.name}.")
        
    metrics = {
        'attendance_percentage': attendance.attendance_percentage,
        'assignment_average': academic.assignment_average,
        'quiz_average': academic.quiz_average,
        'midterm_marks': academic.midterm_marks,
        'practical_marks': academic.practical_marks,
        'project_marks': academic.project_marks,
        'previous_gpa': student.previous_gpa,
        'login_frequency': lms.login_frequency,
        'materials_accessed': lms.materials_accessed,
        'quiz_attempts': lms.quiz_attempts,
        'assignments_submitted': lms.assignments_submitted,
        'total_assignments': lms.total_assignments,
        'late_submissions': lms.late_submissions,
        'consecutive_absences': attendance.consecutive_absences,
        'discussion_participation': lms.discussion_participation,
        'time_spent': lms.time_spent
    }
    
    return metrics, student

def generate_and_save_prediction(student_db_id):
    """
    Fetch current student metrics, run regression & classification predictions,
    explain factors, suggest interventions, and log the results to the database.
    """
    # 1. Fetch metrics
    metrics, student = get_latest_student_metrics(student_db_id)
    
    # 2. Run ML models
    pred_res = predict_student_performance(metrics)
    
    # 3. Explain model decisions (attributions)
    explanation_meta = explain_prediction(metrics, pred_res)
    increasing_factors = explanation_meta['risk_increasing_factors']
    reducing_factors = explanation_meta['risk_reducing_factors']
    
    # 4. Generate plain language explanation (fallback / GenAI)
    explanation_text = generate_genai_explanation(
        pred_res['engineered_features'],
        pred_res['risk_level'],
        pred_res['risk_probability'],
        pred_res['predicted_marks'],
        increasing_factors,
        reducing_factors
    )
    
    # 5. Formulate recommendations
    recommendations_list = suggest_interventions(pred_res['engineered_features'], pred_res['risk_level'])
    
    # 6. Save prediction history to SQLite (Do not overwrite old ones)
    prediction_record = Prediction(
        student_id=student.id,
        predicted_marks=pred_res['predicted_marks'],
        risk_probability=pred_res['risk_probability'],
        completion_probability=pred_res['completion_probability'],
        risk_level=pred_res['risk_level'],
        important_features=json.dumps({
            'increasing_factors': increasing_factors,
            'reducing_factors': reducing_factors,
            'attributions': explanation_meta.get('attributions', {})
        }),
        explanation=explanation_text,
        recommendations=json.dumps(recommendations_list),
        prediction_date=datetime.utcnow(),
        model_version="1.0.0"
    )
    
    db.session.add(prediction_record)
    db.session.commit()
    
    return prediction_record
