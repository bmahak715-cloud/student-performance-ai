import pytest
from utils.database import Educator, db

def test_educator_registration(client, app):
    """Test standard educator registration process."""
    # POST to registration
    response = client.post('/register', data={
        'name': 'Dr. Alice Smith',
        'email': 'alice@college.edu',
        'password': 'Password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Account registered successfully! Please log in." in response.data
    
    # Verify educator saved in DB
    with app.app_context():
        educator = Educator.query.filter_by(email='alice@college.edu').first()
        assert educator is not None
        assert educator.name == 'Dr. Alice Smith'
        assert educator.check_password('Password123')

def test_duplicate_email_registration(client, app, seeded_educator):
    """Test duplicate educator accounts are prevented."""
    response = client.post('/register', data={
        'name': 'Duplicate User',
        'email': 'test@college.edu', # Email already seeded in conftest
        'password': 'Password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"An educator account with this email already exists." in response.data

def test_educator_login_logout(client, app, seeded_educator):
    """Test educator login with valid credentials and logout."""
    # 1. Login attempt
    response = client.post('/login', data={
        'email': 'test@college.edu',
        'password': 'Password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Welcome back, Test Educator!" in response.data
    
    # Verify session active
    with client.session_transaction() as sess:
        assert sess['educator_id'] == seeded_educator.id
        
    # 2. Logout
    logout_resp = client.get('/logout', follow_redirects=True)
    assert logout_resp.status_code == 200
    assert b"You have been logged out." in logout_resp.data
    
    with client.session_transaction() as sess:
        assert 'educator_id' not in sess

def test_unauthorized_route_guards(client):
    """Verify unauthorized page access is blocked and redirected to login."""
    response = client.get('/', follow_redirects=True)
    assert response.status_code == 200
    assert b"Please log in to access this page." in response.data
