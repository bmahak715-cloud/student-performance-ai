from datetime import datetime
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from routes.auth_routes import login_required
from utils.database import db, Student, Intervention, Educator

intervention_bp = Blueprint('intervention', __name__)

@intervention_bp.route('/interventions')
@login_required
def list_interventions():
    """HTML route to view all logged interventions with search/filter features."""
    status_filter = request.args.get('status', '').strip()
    type_filter = request.args.get('type', '').strip()
    
    query = Intervention.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    if type_filter:
        query = query.filter(Intervention.intervention_type.like(f"%{type_filter}%"))
        
    all_interventions = query.order_by(Intervention.intervention_date.desc()).all()
    
    supported_types = [
        "Academic counselling", "Subject tutoring", "Peer mentoring", 
        "Remedial classes", "Assignment recovery plan", "Attendance support", 
        "Study planning", "Follow-up meeting"
    ]
    
    return render_template(
        'interventions.html',
        interventions=all_interventions,
        status=status_filter,
        type=type_filter,
        supported_types=supported_types
    )

@intervention_bp.route('/students/<int:student_db_id>/interventions/add', methods=['POST'])
@login_required
def add_intervention_view(student_db_id):
    """HTML Form submission route to add a student intervention."""
    student = Student.query.get_or_404(student_db_id)
    
    i_type = request.form.get('intervention_type', '').strip()
    desc = request.form.get('description', '').strip()
    follow_up_str = request.form.get('follow_up_date', '').strip()
    
    if not i_type or not desc:
        flash("Intervention Type and Description are required.", "danger")
        return redirect(url_for('student.show_student', student_db_id=student.id))
        
    follow_up_date = None
    if follow_up_str:
        try:
            follow_up_date = datetime.strptime(follow_up_str, "%Y-%m-%d")
        except ValueError:
            flash("Invalid date format for Follow-up Date. Use YYYY-MM-DD.", "danger")
            return redirect(url_for('student.show_student', student_db_id=student.id))
            
    try:
        new_int = Intervention(
            student_id=student.id,
            educator_id=session['educator_id'],
            intervention_type=i_type,
            description=desc,
            follow_up_date=follow_up_date,
            status='Planned',
            intervention_date=datetime.utcnow()
        )
        db.session.add(new_int)
        db.session.commit()
        flash("Intervention successfully registered!", "success")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while logging the intervention.", "danger")
        print(f"Intervention view exception: {e}")
        
    return redirect(url_for('student.show_student', student_db_id=student.id))

@intervention_bp.route('/interventions/<int:int_id>/update', methods=['POST'])
@login_required
def update_intervention_view(int_id):
    """HTML form submission route to update status and outcome notes for an intervention."""
    intervention = Intervention.query.get_or_404(int_id)
    
    status = request.form.get('status', '').strip()
    outcome_notes = request.form.get('outcome_notes', '').strip()
    
    valid_statuses = ['Planned', 'In Progress', 'Completed', 'Cancelled']
    if status not in valid_statuses:
        flash("Invalid intervention status selected.", "danger")
        return redirect(url_for('student.show_student', student_db_id=intervention.student_id))
        
    try:
        intervention.status = status
        if outcome_notes:
            intervention.outcome_notes = outcome_notes
        db.session.commit()
        flash("Intervention status updated successfully!", "success")
    except Exception:
        db.session.rollback()
        flash("An error occurred while updating the intervention.", "danger")
        
    return redirect(url_for('student.show_student', student_db_id=intervention.student_id))


# --- REST API ENDPOINTS ---

@intervention_bp.route('/api/students/<string:student_id>/interventions', methods=['POST'])
def api_add_intervention(student_id):
    """
    POST /api/students/<student_id>/interventions
    REST API endpoint to register a new intervention for a student ID.
    Accepts JSON: { "educator_email": "...", "intervention_type": "...", "description": "...", "follow_up_date": "YYYY-MM-DD" }
    """
    student = Student.query.filter_by(student_id=student_id).first()
    if not student:
        try:
            student = Student.query.get(int(student_id))
        except (ValueError, TypeError):
            student = None
            
    if not student:
        return jsonify({'error': f"Student with ID '{student_id}' not found."}), 404
        
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Missing request body. JSON payload expected.'}), 400
        
    i_type = data.get('intervention_type', '').strip()
    desc = data.get('description', '').strip()
    educator_email = data.get('educator_email', '').strip()
    follow_up_str = data.get('follow_up_date', '').strip()
    
    if not i_type or not desc or not educator_email:
        return jsonify({'error': 'Fields intervention_type, description, and educator_email are required.'}), 400
        
    educator = Educator.query.filter_by(email=educator_email).first()
    if not educator:
        return jsonify({'error': f"Educator with email '{educator_email}' not found."}), 404
        
    follow_up_date = None
    if follow_up_str:
        try:
            follow_up_date = datetime.strptime(follow_up_str, "%Y-%m-%d")
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD.'}), 400
            
    try:
        new_int = Intervention(
            student_id=student.id,
            educator_id=educator.id,
            intervention_type=i_type,
            description=desc,
            follow_up_date=follow_up_date,
            status=data.get('status', 'Planned'),
            intervention_date=datetime.utcnow()
        )
        db.session.add(new_int)
        db.session.commit()
        
        return jsonify({
            'message': 'Intervention registered successfully',
            'intervention_id': new_int.id,
            'student_id': student.student_id,
            'status': new_int.status
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to save intervention', 'details': str(e)}), 500


@intervention_bp.route('/api/students/<string:student_id>/interventions', methods=['GET'])
def api_get_interventions(student_id):
    """
    GET /api/students/<student_id>/interventions
    REST API endpoint listing complete intervention logs for a student ID.
    """
    student = Student.query.filter_by(student_id=student_id).first()
    if not student:
        try:
            student = Student.query.get(int(student_id))
        except (ValueError, TypeError):
            student = None
            
    if not student:
        return jsonify({'error': f"Student with ID '{student_id}' not found."}), 404
        
    interventions = Intervention.query.filter_by(student_id=student.id).order_by(Intervention.intervention_date.desc()).all()
    
    results = []
    for item in interventions:
        # Load educator details
        ed = Educator.query.get(item.educator_id)
        ed_name = ed.name if ed else "Unknown Educator"
        
        results.append({
            'intervention_id': item.id,
            'educator_name': ed_name,
            'intervention_type': item.intervention_type,
            'description': item.description,
            'intervention_date': item.intervention_date.isoformat(),
            'follow_up_date': item.follow_up_date.strftime("%Y-%m-%d") if item.follow_up_date else None,
            'status': item.status,
            'outcome_notes': item.outcome_notes
        })
        
    return jsonify({
        'student_id': student.student_id,
        'student_name': student.name,
        'interventions': results
    }), 200
