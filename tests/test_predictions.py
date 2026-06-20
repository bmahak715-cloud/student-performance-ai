import pytest
import json
from unittest.mock import patch
from utils.database import db, Student, AcademicRecord, Attendance, LMSEngagement

def test_prediction_api_missing_fields(client):
    """Test API validations on missing parameters."""
    response = client.post('/api/predict', 
                           data=json.dumps({'name': 'Incomplete'}), 
                           content_type='application/json')
    
    assert response.status_code == 400
    res_data = json.loads(response.data)
    assert 'validation_errors' in res_data

@patch('ml.predict.predict_student_performance')
@patch('ml.explain.explain_prediction')
def test_prediction_api_success(mock_explain, mock_predict, client):
    """Test successful model predictions via POST /api/predict using mocked ML engine."""
    mock_predict.return_value = {
        'predicted_marks': 75.0,
        'risk_probability': 0.15,
        'risk_level': 'Low',
        'completion_probability': 85.0,
        'engineered_features': {'attendance_percentage': 90, 'assignments_submitted': 5, 'total_assignments': 5}
    }
    
    mock_explain.return_value = {
        'risk_increasing_factors': [],
        'risk_reducing_factors': ['Consistent class attendance (90.0%)'],
        'attributions': {}
    }
    
    # Valid payload
    payload = {
        'student_id': 'STU7000',
        'name': 'Model Student',
        'age': 20,
        'course': 'Computer Science',
        'semester': 4,
        'section': 'A',
        'previous_gpa': 3.4,
        
        'assignment_average': 85.0,
        'quiz_average': 80.0,
        'midterm_marks': 75.0,
        'practical_marks': 80.0,
        'project_marks': 90.0,
        'previous_result': 85.0,
        
        'total_classes': 20,
        'attended_classes': 18,
        'consecutive_absences': 0,
        'late_arrivals': 0,
        
        'login_frequency': 8,
        'materials_accessed': 50,
        'quiz_attempts': 4,
        'assignments_submitted': 5,
        'total_assignments': 5,
        'late_submissions': 0,
        'time_spent': 15.0,
        'discussion_participation': 3
    }
    
    response = client.post('/api/predict', 
                           data=json.dumps(payload), 
                           content_type='application/json')
    
    assert response.status_code == 200
    res_data = json.loads(response.data)
    
    assert res_data['predicted_marks'] == 75.0
    assert res_data['risk_level'] == 'Low'
    assert res_data['risk_probability'] == 0.15
    assert 'Consistent class attendance' in res_data['important_features']['reducing'][0]

def test_risk_level_calculation_logic():
    """Verify threshold limits for Low, Medium, and High risk classifications."""
    # Custom helper test since predictions utilize threshold constants
    from config import Config
    
    def check_risk_level(prob):
        if prob < Config.RISK_LOW_THRESHOLD:
            return 'Low'
        elif prob > Config.RISK_HIGH_THRESHOLD:
            return 'High'
        return 'Medium'
        
    assert check_risk_level(0.10) == 'Low'
    assert check_risk_level(0.29) == 'Low'
    assert check_risk_level(0.30) == 'Medium'
    assert check_risk_level(0.50) == 'Medium'
    assert check_risk_level(0.60) == 'Medium'
    assert check_risk_level(0.61) == 'High'
    assert check_risk_level(0.95) == 'High'
