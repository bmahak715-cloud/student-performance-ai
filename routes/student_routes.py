from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from routes.auth_routes import login_required
from utils.database import db, Student, AcademicRecord, Attendance, LMSEngagement, Prediction, Intervention
from utils.validators import (
    validate_student_data, 
    validate_academic_record, 
    validate_attendance_record, 
    validate_lms_engagement
)

student_bp = Blueprint('student', __name__)

@student_bp.route('/students')
@login_required
def list_students():
    """List all students with search, risk filters, and pagination."""
    search_query = request.args.get('search', '').strip()
    risk_filter = request.args.get('risk', '').strip().lower()
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Base query
    query = Student.query
    
    if search_query:
        query = query.filter(
            (Student.name.like(f"%{search_query}%")) | 
            (Student.student_id.like(f"%{search_query}%")) |
            (Student.course.like(f"%{search_query}%"))
        )
        
    all_matching = query.all()
    filtered_students = []
    
    # Filter by risk requires checking the latest prediction
    for student in all_matching:
        latest_pred = Prediction.query.filter_by(student_id=student.id).order_by(Prediction.prediction_date.desc()).first()
        latest_att = Attendance.query.filter_by(student_id=student.id).order_by(Attendance.record_date.desc()).first()
        
        stud_risk = 'unpredicted'
        if latest_pred:
            stud_risk = latest_pred.risk_level.lower()
            
        if not risk_filter or stud_risk == risk_filter:
            filtered_students.append((student, latest_pred, latest_att))
            
    # Simple manual pagination on list of tuples
    total_items = len(filtered_students)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_items = filtered_students[start_idx:end_idx]
    
    total_pages = (total_items + per_page - 1) // per_page
    
    return render_template(
        'students.html',
        students=paginated_items,
        search=search_query,
        risk=risk_filter,
        page=page,
        total_pages=total_pages,
        total_students=total_items
    )

@student_bp.route('/students/add', methods=['GET', 'POST'])
@login_required
def add_student():
    """Add new student and their initial academic/attendance/LMS records."""
    if request.method == 'POST':
        # Metadata
        student_id = request.form.get('student_id', '').strip().upper()
        name = request.form.get('name', '').strip()
        age = request.form.get('age', '')
        course = request.form.get('course', '').strip()
        semester = request.form.get('semester', '')
        section = request.form.get('section', '').strip().upper()
        previous_gpa = request.form.get('previous_gpa', '')
        
        # Initial logs (if provided, otherwise defaults)
        assignment_avg = request.form.get('assignment_average', '70.0')
        quiz_avg = request.form.get('quiz_average', '70.0')
        midterm = request.form.get('midterm_marks', '70.0')
        practical = request.form.get('practical_marks', '70.0')
        project = request.form.get('project_marks', '70.0')
        prev_res = request.form.get('previous_result', '70.0')
        
        total_classes = request.form.get('total_classes', '10')
        attended_classes = request.form.get('attended_classes', '9')
        consec_abs = request.form.get('consecutive_absences', '0')
        late_arr = request.form.get('late_arrivals', '0')
        
        login_freq = request.form.get('login_frequency', '5')
        mat_access = request.form.get('materials_accessed', '20')
        quiz_att = request.form.get('quiz_attempts', '2')
        assign_sub = request.form.get('assignments_submitted', '5')
        tot_assign = request.form.get('total_assignments', '5')
        late_sub = request.form.get('late_submissions', '0')
        time_spent = request.form.get('time_spent', '10.0')
        disc_part = request.form.get('discussion_participation', '2')
        
        # Validations
        errors = validate_student_data(student_id, name, age, course, semester, section, previous_gpa)
        acad_errors = validate_academic_record(assignment_avg, quiz_avg, midterm, practical, project, prev_res)
        att_errors = validate_attendance_record(total_classes, attended_classes, consec_abs, late_arr)
        lms_errors = validate_lms_engagement(login_freq, mat_access, quiz_att, assign_sub, tot_assign, late_sub, time_spent, disc_part)
        
        errors.extend(acad_errors)
        errors.extend(att_errors)
        errors.extend(lms_errors)
        
        # Check duplicate ID
        existing = Student.query.filter_by(student_id=student_id).first()
        if existing:
            errors.append(f"A student with Institutional ID {student_id} already exists.")
            
        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template('add_student.html', form_data=request.form)
            
        try:
            # Create Student
            new_student = Student(
                student_id=student_id, name=name, age=int(age), course=course,
                semester=int(semester), section=section, previous_gpa=float(previous_gpa)
            )
            db.session.add(new_student)
            db.session.commit()
            
            # Create Academic Record
            new_acad = AcademicRecord(
                student_id=new_student.id,
                assignment_average=float(assignment_avg),
                quiz_average=float(quiz_avg),
                midterm_marks=float(midterm),
                practical_marks=float(practical),
                project_marks=float(project),
                previous_result=float(prev_res)
            )
            
            # Create Attendance Log
            tot_cls_val = int(total_classes)
            att_cls_val = int(attended_classes)
            new_att = Attendance(
                student_id=new_student.id,
                total_classes=tot_cls_val,
                attended_classes=att_cls_val,
                attendance_percentage=(att_cls_val / tot_cls_val) * 100,
                consecutive_absences=int(consec_abs),
                late_arrivals=int(late_arr)
            )
            
            # Create LMS engagement log
            new_lms = LMSEngagement(
                student_id=new_student.id,
                login_frequency=int(login_freq),
                materials_accessed=int(mat_access),
                quiz_attempts=int(quiz_att),
                assignments_submitted=int(assign_sub),
                total_assignments=int(tot_assign),
                late_submissions=int(late_sub),
                time_spent=float(time_spent),
                discussion_participation=int(disc_part)
            )
            
            db.session.add(new_acad)
            db.session.add(new_att)
            db.session.add(new_lms)
            db.session.commit()
            
            flash(f"Student {name} added successfully with baseline academic logs!", "success")
            return redirect(url_for('student.show_student', student_db_id=new_student.id))
            
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while creating records. Please try again.", "danger")
            print(f"Error creating student: {e}")
            
    return render_template('add_student.html')

@student_bp.route('/students/<int:student_db_id>')
@login_required
def show_student(student_db_id):
    """View complete profile of a single student with charts and timeline logs."""
    student = Student.query.get_or_4_4_0 = Student.query.get(student_db_id)
    if not student:
        flash("Student record not found.", "danger")
        return redirect(url_for('student.list_students'))
        
    academic_history = AcademicRecord.query.filter_by(student_id=student.id).order_by(AcademicRecord.record_date.asc()).all()
    attendance_history = Attendance.query.filter_by(student_id=student.id).order_by(Attendance.record_date.asc()).all()
    lms_history = LMSEngagement.query.filter_by(student_id=student.id).order_by(LMSEngagement.record_date.asc()).all()
    predictions = Prediction.query.filter_by(student_id=student.id).order_by(Prediction.prediction_date.desc()).all()
    interventions = Intervention.query.filter_by(student_id=student.id).order_by(Intervention.intervention_date.desc()).all()
    
    # Grab latest metrics
    latest_acad = academic_history[-1] if academic_history else None
    latest_att = attendance_history[-1] if attendance_history else None
    latest_lms = lms_history[-1] if lms_history else None
    latest_pred = predictions[0] if predictions else None
    
    # Compile chart lists
    timeline_dates = [item.record_date.strftime("%b %d") for item in academic_history]
    
    marks_trend = [round((item.assignment_average + item.quiz_average + item.midterm_marks) / 3, 1) for item in academic_history]
    attendance_trend = [round(item.attendance_percentage, 1) for item in attendance_history]
    lms_logins_trend = [item.login_frequency for item in lms_history]
    lms_hours_trend = [round(item.time_spent, 1) for item in lms_history]
    
    risk_trend_dates = [item.prediction_date.strftime("%b %d %H:%M") for item in reversed(predictions)]
    risk_probabilities = [round(item.risk_probability * 100, 1) for item in reversed(predictions)]
    
    chart_data = {
        'dates': timeline_dates,
        'marks': marks_trend,
        'attendance': attendance_trend,
        'logins': lms_logins_trend,
        'hours': lms_hours_trend,
        'risk_dates': risk_trend_dates,
        'risk_probs': risk_probabilities
    }
    
    # Supported interventions list for quick dropdowns
    supported_interventions = [
        "Academic counselling", "Subject tutoring", "Peer mentoring", 
        "Remedial classes", "Assignment recovery plan", "Attendance support", 
        "Study planning", "Follow-up meeting"
    ]
    
    return render_template(
        'student_details.html',
        student=student,
        academic=latest_acad,
        attendance=latest_att,
        lms=latest_lms,
        prediction=latest_pred,
        academic_history=academic_history,
        attendance_history=attendance_history,
        lms_history=lms_history,
        predictions=predictions,
        interventions=interventions,
        chart_data=chart_data,
        supported_interventions=supported_interventions
    )

@student_bp.route('/students/<int:student_db_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_student(student_db_id):
    """Edit student metadata details."""
    student = Student.query.get_or_404(student_db_id)
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        age = request.form.get('age', '')
        course = request.form.get('course', '').strip()
        semester = request.form.get('semester', '')
        section = request.form.get('section', '').strip().upper()
        previous_gpa = request.form.get('previous_gpa', '')
        
        errors = validate_student_data(student.student_id, name, age, course, semester, section, previous_gpa)
        
        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template('edit_student.html', student=student)
            
        try:
            student.name = name
            student.age = int(age)
            student.course = course
            student.semester = int(semester)
            student.section = section
            student.previous_gpa = float(previous_gpa)
            
            db.session.commit()
            flash("Student profile updated successfully!", "success")
            return redirect(url_for('student.show_student', student_db_id=student.id))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred during update. Please try again.", "danger")
            
    return render_template('edit_student.html', student=student)

@student_bp.route('/students/<int:student_db_id>/delete', methods=['POST'])
@login_required
def delete_student(student_db_id):
    """Delete student and all cascades."""
    student = Student.query.get_or_404(student_db_id)
    name = student.name
    try:
        db.session.delete(student)
        db.session.commit()
        flash(f"Student {name} and all related logs were deleted.", "info")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred during deletion. Please try again.", "danger")
        
    return redirect(url_for('student.list_students'))

@student_bp.route('/students/<int:student_db_id>/academic/add', methods=['POST'])
@login_required
def add_academic_record(student_db_id):
    """Add a new academic log."""
    student = Student.query.get_or_404(student_db_id)
    
    assign_avg = request.form.get('assignment_average', '')
    quiz_avg = request.form.get('quiz_average', '')
    midterm = request.form.get('midterm_marks', '')
    practical = request.form.get('practical_marks', '')
    project = request.form.get('project_marks', '')
    prev_res = request.form.get('previous_result', '')
    
    errors = validate_academic_record(assign_avg, quiz_avg, midterm, practical, project, prev_res)
    if errors:
        for err in errors:
            flash(err, "danger")
        return redirect(url_for('student.show_student', student_db_id=student.id))
        
    try:
        acad = AcademicRecord(
            student_id=student.id,
            assignment_average=float(assign_avg),
            quiz_average=float(quiz_avg),
            midterm_marks=float(midterm),
            practical_marks=float(practical),
            project_marks=float(project),
            previous_result=float(prev_res)
        )
        db.session.add(acad)
        db.session.commit()
        flash("Academic record logged successfully!", "success")
    except Exception:
        db.session.rollback()
        flash("An error occurred while logging the academic record.", "danger")
        
    return redirect(url_for('student.show_student', student_db_id=student.id))

@student_bp.route('/students/<int:student_db_id>/attendance/add', methods=['POST'])
@login_required
def add_attendance_record(student_db_id):
    """Add a new attendance log."""
    student = Student.query.get_or_404(student_db_id)
    
    total_classes = request.form.get('total_classes', '')
    attended_classes = request.form.get('attended_classes', '')
    consec_abs = request.form.get('consecutive_absences', '0')
    late_arr = request.form.get('late_arrivals', '0')
    
    errors = validate_attendance_record(total_classes, attended_classes, consec_abs, late_arr)
    if errors:
        for err in errors:
            flash(err, "danger")
        return redirect(url_for('student.show_student', student_db_id=student.id))
        
    try:
        tot = int(total_classes)
        att = int(attended_classes)
        attendance = Attendance(
            student_id=student.id,
            total_classes=tot,
            attended_classes=att,
            attendance_percentage=(att / tot) * 100,
            consecutive_absences=int(consec_abs),
            late_arrivals=int(late_arr)
        )
        db.session.add(attendance)
        db.session.commit()
        flash("Attendance log logged successfully!", "success")
    except Exception:
        db.session.rollback()
        flash("An error occurred while logging the attendance details.", "danger")
        
    return redirect(url_for('student.show_student', student_db_id=student.id))

@student_bp.route('/students/<int:student_db_id>/lms/add', methods=['POST'])
@login_required
def add_lms_record(student_db_id):
    """Add a new LMS engagement log."""
    student = Student.query.get_or_404(student_db_id)
    
    login_freq = request.form.get('login_frequency', '')
    mat_access = request.form.get('materials_accessed', '')
    quiz_att = request.form.get('quiz_attempts', '')
    assign_sub = request.form.get('assignments_submitted', '')
    tot_assign = request.form.get('total_assignments', '')
    late_sub = request.form.get('late_submissions', '0')
    time_spent = request.form.get('time_spent', '')
    disc_part = request.form.get('discussion_participation', '0')
    
    errors = validate_lms_engagement(login_freq, mat_access, quiz_att, assign_sub, tot_assign, late_sub, time_spent, disc_part)
    if errors:
        for err in errors:
            flash(err, "danger")
        return redirect(url_for('student.show_student', student_db_id=student.id))
        
    try:
        lms = LMSEngagement(
            student_id=student.id,
            login_frequency=int(login_freq),
            materials_accessed=int(mat_access),
            quiz_attempts=int(quiz_att),
            assignments_submitted=int(assign_sub),
            total_assignments=int(tot_assign),
            late_submissions=int(late_sub),
            time_spent=float(time_spent),
            discussion_participation=int(disc_part)
        )
        db.session.add(lms)
        db.session.commit()
        flash("LMS activity log registered successfully!", "success")
    except Exception:
        db.session.rollback()
        flash("An error occurred while registering the LMS log.", "danger")
        
    return redirect(url_for('student.show_student', student_db_id=student.id))
