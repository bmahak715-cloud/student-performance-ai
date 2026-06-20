import pytest
from utils.database import db, Student, Attendance

def test_student_creation(client, app, seeded_educator):
    """Test creating student profiles and validating inputs."""
    # Establish session
    with client.session_transaction() as sess:
        sess['educator_id'] = seeded_educator.id
        sess['educator_name'] = seeded_educator.name
        
    response = client.post('/students/add', data={
        'student_id': 'STU5050',
        'name': 'Bob Ross',
        'age': '22',
        'course': 'Arts & Science',
        'semester': '3',
        'section': 'B',
        'previous_gpa': '3.20',
        
        # Initial logs
        'assignment_average': '80.0',
        'quiz_average': '75.0',
        'midterm_marks': '75.0',
        'practical_marks': '85.0',
        'project_marks': '90.0',
        'previous_result': '80.0',
        
        'total_classes': '20',
        'attended_classes': '18',
        'consecutive_absences': '0',
        'late_arrivals': '1',
        
        'login_frequency': '6',
        'materials_accessed': '30',
        'quiz_attempts': '4',
        'assignments_submitted': '5',
        'total_assignments': '5',
        'late_submissions': '0',
        'time_spent': '15.0',
        'discussion_participation': '2'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Student Bob Ross added successfully" in response.data
    
    # Check DB
    with app.app_context():
        student = Student.query.filter_by(student_id='STU5050').first()
        assert student is not None
        assert student.name == 'Bob Ross'
        
        # Verify attendance log percentages
        att = Attendance.query.filter_by(student_id=student.id).first()
        assert att is not None
        assert att.attendance_percentage == 90.0

def test_student_editing(client, app, seeded_educator):
    """Test updating student details."""
    with app.app_context():
        student = Student(student_id='STU9999', name='Original Name', age=20, course='CS', semester=2, section='A', previous_gpa=3.0)
        db.session.add(student)
        db.session.commit()
        student_id = student.id
        
    with client.session_transaction() as sess:
        sess['educator_id'] = seeded_educator.id
        
    response = client.post(f'/students/{student_id}/edit', data={
        'name': 'Updated Name',
        'age': '21',
        'course': 'Software Eng',
        'semester': '3',
        'section': 'B',
        'previous_gpa': '3.50'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Student profile updated successfully" in response.data
    
    with app.app_context():
        updated_student = Student.query.get(student_id)
        assert updated_student.name == 'Updated Name'
        assert updated_student.age == 21
        assert updated_student.previous_gpa == 3.50

def test_invalid_attendance_validation(client, app, seeded_educator):
    """Test validation errors for invalid attendance metrics (e.g. attended > total classes)."""
    with client.session_transaction() as sess:
        sess['educator_id'] = seeded_educator.id
        
    response = client.post('/students/add', data={
        'student_id': 'STU4040',
        'name': 'Failed Student',
        'age': '20',
        'course': 'Arts',
        'semester': '2',
        'section': 'A',
        'previous_gpa': '2.50',
        
        'total_classes': '10',
        'attended_classes': '15', # Attended > Total! Invalid!
        'consecutive_absences': '-1', # Negative! Invalid!
        
        # Remainder
        'assignment_average': '70.0', 'quiz_average': '70.0', 'midterm_marks': '70.0', 'practical_marks': '70.0', 'project_marks': '70.0', 'previous_result': '70.0',
        'late_arrivals': '0', 'login_frequency': '5', 'materials_accessed': '10', 'quiz_attempts': '1', 'assignments_submitted': '2', 'total_assignments': '2', 'late_submissions': '0', 'time_spent': '5.0', 'discussion_participation': '0'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Attended classes cannot be greater than total classes." in response.data
    assert b"Consecutive absences cannot be negative." in response.data
