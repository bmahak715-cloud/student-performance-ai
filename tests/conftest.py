import pytest
from app import create_app
from utils.database import db, Educator, Student

@pytest.fixture
def app():
    """Create and configure a new Flask app instance for testing."""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key-aura'
    })
    
    # Initialize the database and tables
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def seeded_educator(app):
    """Create a default educator account in the test database."""
    with app.app_context():
        educator = Educator(name="Test Educator", email="test@college.edu")
        educator.set_password("Password123")
        db.session.add(educator)
        db.session.commit()
        return educator
