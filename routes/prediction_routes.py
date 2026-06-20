import json
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from routes.auth_routes import login_required
from utils.database import Student, Prediction
from services.prediction_service import generate_and_save_prediction
from ml.predict import predict_student_performance
from ml.explain import explain_prediction
from services.explanation_service import generate_genai_explanation
from services.intervention_service import suggest_interventions
from utils.validators import (
    validate_student_data, 
    validate_academic_record, 
    validate_attendance_record, 
    validate_lms_engagement
)

prediction_bp = Blueprint('prediction', __name__)

@prediction_bp.route('/students/<int:student_db_id>/predict', methods=['POST', 'GET'])
@login_required
def run_prediction_view(student_db_id):
    """Trigger a new ML prediction run for a student and redirect back to their details page."""
    try:
        generate_and_save_prediction(student_db_id)
        flash("New prediction generated successfully using the latest student metrics!", "success")
    except ValueError as val_err:
        flash(str(val_err), "warning")
    except FileNotFoundError as fnf_err:
        flash(f"ML Pipeline Error: {str(fnf_err)}", "danger")
    except Exception as e:
        flash("An unexpected error occurred during prediction generation.", "danger")
        print(f"Prediction view exception: {e}")
        
    return redirect(url_for('student.show_student', student_db_id=student_db_id))


# --- REST API ENDPOINTS ---

@prediction_bp.route('/api/predict', methods=['POST'])
def api_predict():
    """
    POST /api/predict
    REST API endpoint for real-time model inference.
    Accepts JSON containing all student, academic, attendance, and LMS attributes.
    Returns JSON prediction report.
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Missing request body. JSON payload expected.'}), 400
        
    # Validate JSON values
    # Extract values
    student_id = data.get('student_id', 'API-TEMP').strip().upper()
    name = data.get('name', 'API Student').strip()
    age = data.get('age', 20)
    course = data.get('course', 'CS').strip()
    semester = data.get('semester', 1)
    section = data.get('section', 'A').strip().upper()
    previous_gpa = data.get('previous_gpa', 3.0)
    
    assignment_avg = data.get('assignment_average', 70.0)
    quiz_avg = data.get('quiz_average', 70.0)
    midterm = data.get('midterm_marks', 70.0)
    practical = data.get('practical_marks', 70.0)
    project = data.get('project_marks', 70.0)
    prev_res = data.get('previous_result', 70.0)
    
    total_classes = data.get('total_classes', 10)
    attended_classes = data.get('attended_classes', 9)
    consec_abs = data.get('consecutive_absences', 0)
    late_arr = data.get('late_arrivals', 0)
    
    login_freq = data.get('login_frequency', 5)
    mat_access = data.get('materials_accessed', 20)
    quiz_att = data.get('quiz_attempts', 2)
    assign_sub = data.get('assignments_submitted', 5)
    tot_assign = data.get('total_assignments', 5)
    late_sub = data.get('late_submissions', 0)
    time_spent = data.get('time_spent', 10.0)
    disc_part = data.get('discussion_participation', 2)
    
    # Run validations
    errors = validate_student_data(student_id, name, age, course, semester, section, previous_gpa)
    errors.extend(validate_academic_record(assignment_avg, quiz_avg, midterm, practical, project, prev_res))
    errors.extend(validate_attendance_record(total_classes, attended_classes, consec_abs, late_arr))
    errors.extend(validate_lms_engagement(login_freq, mat_access, quiz_att, assign_sub, tot_assign, late_sub, time_spent, disc_part))
    
    if errors:
        return jsonify({'error': 'Validation failed', 'validation_errors': errors}), 400
        
    try:
        # Build features dict for prediction
        # Standardized keys
        metrics = {
            'attendance_percentage': (float(attended_classes) / float(total_classes)) * 100,
            'assignment_average': float(assignment_avg),
            'quiz_average': float(quiz_avg),
            'midterm_marks': float(midterm),
            'practical_marks': float(practical),
            'project_marks': float(project),
            'previous_gpa': float(previous_gpa),
            'login_frequency': int(login_freq),
            'materials_accessed': int(mat_access),
            'quiz_attempts': int(quiz_att),
            'assignments_submitted': int(assign_sub),
            'total_assignments': int(tot_assign),
            'late_submissions': int(late_sub),
            'consecutive_absences': int(consec_abs),
            'discussion_participation': int(disc_part),
            'time_spent': float(time_spent)
        }
        
        # 1. Run ML
        pred_res = predict_student_performance(metrics)
        
        # 2. Get local attributions
        explanation_meta = explain_prediction(metrics, pred_res)
        increasing_factors = explanation_meta['risk_increasing_factors']
        reducing_factors = explanation_meta['risk_reducing_factors']
        
        # 3. Generate explanation text
        explanation_text = generate_genai_explanation(
            pred_res['engineered_features'],
            pred_res['risk_level'],
            pred_res['risk_probability'],
            pred_res['predicted_marks'],
            increasing_factors,
            reducing_factors
        )
        
        # 4. Formulate recommendations
        recommendations = suggest_interventions(pred_res['engineered_features'], pred_res['risk_level'])
        
        return jsonify({
            'predicted_marks': pred_res['predicted_marks'],
            'risk_probability': pred_res['risk_probability'],
            'risk_level': pred_res['risk_level'],
            'completion_probability': pred_res['completion_probability'],
            'important_features': {
                'increasing': increasing_factors,
                'reducing': reducing_factors
            },
            'explanation': explanation_text,
            'recommendations': recommendations,
            'model_version': '1.0.0'
        }), 200
        
    except FileNotFoundError as fnf_e:
        return jsonify({
            'error': 'Predictive model assets are not trained/configured on the server.',
            'details': str(fnf_e)
        }), 503
    except Exception as e:
        return jsonify({
            'error': 'An internal processing error occurred during prediction.',
            'details': str(e)
        }), 500


@prediction_bp.route('/api/students/<string:student_id>/predictions', methods=['GET'])
def api_student_predictions_history(student_id):
    """
    GET /api/students/<student_id>/predictions
    REST API endpoint returning complete prediction log history for a student ID.
    """
    student = Student.query.filter_by(student_id=student_id).first()
    if not student:
        # Check by database ID if student_id institutional lookup failed
        try:
            student = Student.query.get(int(student_id))
        except (ValueError, TypeError):
            student = None
            
    if not student:
        return jsonify({'error': f"Student with ID '{student_id}' not found."}), 404
        
    predictions = Prediction.query.filter_by(student_id=student.id).order_by(Prediction.prediction_date.desc()).all()
    
    history = []
    for pred in predictions:
        # Load important features list safely
        try:
            feat = json.loads(pred.important_features)
        except Exception:
            feat = {}
            
        try:
            rec = json.loads(pred.recommendations)
        except Exception:
            rec = []
            
        history.append({
            'prediction_id': pred.id,
            'predicted_marks': pred.predicted_marks,
            'risk_probability': pred.risk_probability,
            'risk_level': pred.risk_level,
            'completion_probability': pred.completion_probability,
            'explanation': pred.explanation,
            'important_features': feat,
            'recommendations': rec,
            'prediction_date': pred.prediction_date.isoformat(),
            'model_version': pred.model_version
        })
        
    return jsonify({
        'student_id': student.student_id,
        'student_name': student.name,
        'predictions': history
    }), 200
