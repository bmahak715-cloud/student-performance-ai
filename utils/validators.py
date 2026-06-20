import re

def validate_email(email):
    """Simple regex check for email format validation."""
    if not email:
        return False
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(email_regex, email))

def validate_password(password):
    """Validate password strength (minimum 6 characters)."""
    if not password or len(password) < 6:
        return False
    return True

def validate_student_data(student_id, name, age, course, semester, section, previous_gpa):
    """Validate student record inputs."""
    errors = []
    
    if not student_id or not student_id.strip():
        errors.append("Student ID is required.")
    elif not re.match(r'^[A-Za-z0-9_-]+$', student_id):
        errors.append("Student ID contains invalid characters. Use letters, numbers, hyphens, and underscores only.")
        
    if not name or not name.strip():
        errors.append("Student Name is required.")
        
    try:
        age_val = int(age)
        if age_val < 15 or age_val > 100:
            errors.append("Student Age must be between 15 and 100.")
    except (ValueError, TypeError):
        errors.append("Student Age must be a valid integer.")
        
    if not course or not course.strip():
        errors.append("Course is required.")
        
    try:
        sem_val = int(semester)
        if sem_val < 1 or sem_val > 10:
            errors.append("Semester must be between 1 and 10.")
    except (ValueError, TypeError):
        errors.append("Semester must be a valid integer.")
        
    if not section or not section.strip():
        errors.append("Section is required.")
        
    try:
        gpa_val = float(previous_gpa)
        if gpa_val < 0.0 or gpa_val > 4.0:
            errors.append("Previous GPA must be between 0.0 and 4.0.")
    except (ValueError, TypeError):
        errors.append("Previous GPA must be a valid decimal number.")
        
    return errors

def validate_academic_record(assignment_average, quiz_average, midterm_marks, practical_marks, project_marks, previous_result):
    """Validate academic marks inputs (must be between 0 and 100)."""
    errors = []
    marks_dict = {
        "Assignment Average": assignment_average,
        "Quiz Average": quiz_average,
        "Midterm Marks": midterm_marks,
        "Practical Marks": practical_marks,
        "Project Marks": project_marks,
        "Previous Course Result": previous_result
    }
    
    for label, val in list(marks_dict.items()):
        try:
            val_float = float(val)
            if val_float < 0.0 or val_float > 100.0:
                errors.append(f"{label} must be between 0.0 and 100.0.")
        except (ValueError, TypeError):
            errors.append(f"{label} must be a valid decimal number.")
            
    return errors

def validate_attendance_record(total_classes, attended_classes, consecutive_absences, late_arrivals):
    """Validate attendance input constraints."""
    errors = []
    
    try:
        tot = int(total_classes)
        att = int(attended_classes)
        
        if tot <= 0:
            errors.append("Total classes must be greater than zero.")
        if att < 0:
            errors.append("Attended classes cannot be negative.")
        if att > tot:
            errors.append("Attended classes cannot be greater than total classes.")
    except (ValueError, TypeError):
        errors.append("Total classes and attended classes must be valid integers.")
        
    try:
        cab = int(consecutive_absences)
        lat = int(late_arrivals)
        if cab < 0:
            errors.append("Consecutive absences cannot be negative.")
        if lat < 0:
            errors.append("Late arrivals cannot be negative.")
    except (ValueError, TypeError):
        errors.append("Consecutive absences and late arrivals must be valid integers.")
        
    return errors

def validate_lms_engagement(login_frequency, materials_accessed, quiz_attempts, assignments_submitted, total_assignments, late_submissions, time_spent, discussion_participation):
    """Validate LMS Engagement input metrics."""
    errors = []
    
    try:
        sub = int(assignments_submitted)
        tot = int(total_assignments)
        if tot < 0:
            errors.append("Total assignments cannot be negative.")
        if sub < 0:
            errors.append("Assignments submitted cannot be negative.")
        if sub > tot:
            errors.append("Assignments submitted cannot be greater than total assignments.")
    except (ValueError, TypeError):
        errors.append("Assignments submitted and total assignments must be valid integers.")
        
    int_fields = {
        "Login Frequency": login_frequency,
        "Materials Accessed": materials_accessed,
        "Quiz Attempts": quiz_attempts,
        "Late Submissions": late_submissions,
        "Discussion Participation": discussion_participation
    }
    
    for label, val in list(int_fields.items()):
        try:
            val_int = int(val)
            if val_int < 0:
                errors.append(f"{label} cannot be negative.")
        except (ValueError, TypeError):
            errors.append(f"{label} must be a valid integer.")
            
    try:
        ts = float(time_spent)
        if ts < 0.0:
            errors.append("Time spent on platform cannot be negative.")
    except (ValueError, TypeError):
        errors.append("Time spent on platform must be a valid decimal number.")
        
    return errors
