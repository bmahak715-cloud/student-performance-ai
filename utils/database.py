from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Educator(db.Model):
    __tablename__ = 'educators'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    interventions = db.relationship('Intervention', backref='educator', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), unique=True, nullable=False, index=True) # Institutional Unique ID
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    course = db.Column(db.String(100), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    section = db.Column(db.String(10), nullable=False)
    previous_gpa = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships (with cascade delete to keep referential integrity)
    academic_records = db.relationship('AcademicRecord', backref='student', cascade='all, delete-orphan', lazy=True)
    attendance_records = db.relationship('Attendance', backref='student', cascade='all, delete-orphan', lazy=True)
    lms_engagements = db.relationship('LMSEngagement', backref='student', cascade='all, delete-orphan', lazy=True)
    predictions = db.relationship('Prediction', backref='student', cascade='all, delete-orphan', lazy=True)
    interventions = db.relationship('Intervention', backref='student', cascade='all, delete-orphan', lazy=True)


class AcademicRecord(db.Model):
    __tablename__ = 'academic_records'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    assignment_average = db.Column(db.Float, nullable=False) # 0 to 100
    quiz_average = db.Column(db.Float, nullable=False)       # 0 to 100
    midterm_marks = db.Column(db.Float, nullable=False)      # 0 to 100
    practical_marks = db.Column(db.Float, nullable=False)    # 0 to 100
    project_marks = db.Column(db.Float, nullable=False)      # 0 to 100
    previous_result = db.Column(db.Float, nullable=False)     # 0 to 100 (marks in prerequisite course)
    record_date = db.Column(db.DateTime, default=datetime.utcnow)


class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    total_classes = db.Column(db.Integer, nullable=False)
    attended_classes = db.Column(db.Integer, nullable=False)
    attendance_percentage = db.Column(db.Float, nullable=False) # attended / total * 100
    consecutive_absences = db.Column(db.Integer, default=0)
    late_arrivals = db.Column(db.Integer, default=0)
    record_date = db.Column(db.DateTime, default=datetime.utcnow)


class LMSEngagement(db.Model):
    __tablename__ = 'lms_engagement'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    login_frequency = db.Column(db.Integer, nullable=False)       # Logins per week
    materials_accessed = db.Column(db.Integer, nullable=False)     # Number of items downloaded/viewed
    quiz_attempts = db.Column(db.Integer, nullable=False)          # Quiz attempts in LMS
    assignments_submitted = db.Column(db.Integer, nullable=False)  # Total submitted
    total_assignments = db.Column(db.Integer, nullable=False)      # Total assigned
    late_submissions = db.Column(db.Integer, default=0)
    time_spent = db.Column(db.Float, nullable=False)               # Hours spent on platform
    discussion_participation = db.Column(db.Integer, default=0)   # Number of posts/replies
    record_date = db.Column(db.DateTime, default=datetime.utcnow)


class Prediction(db.Model):
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    predicted_marks = db.Column(db.Float, nullable=False)
    risk_probability = db.Column(db.Float, nullable=False)       # 0.0 to 1.0 (or percentage)
    completion_probability = db.Column(db.Float, default=100.0)  # Course completion probability
    risk_level = db.Column(db.String(20), nullable=False)         # Low, Medium, High
    important_features = db.Column(db.Text, nullable=False)       # JSON string representing key features impact
    explanation = db.Column(db.Text, nullable=False)              # Natural language summary of risk reasons
    recommendations = db.Column(db.Text, nullable=False)          # Suggested interventions based on profile
    prediction_date = db.Column(db.DateTime, default=datetime.utcnow)
    model_version = db.Column(db.String(50), nullable=False)


class Intervention(db.Model):
    __tablename__ = 'interventions'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    educator_id = db.Column(db.Integer, db.ForeignKey('educators.id'), nullable=False)
    intervention_type = db.Column(db.String(100), nullable=False) # e.g. Academic counselling, Subject tutoring, etc.
    description = db.Column(db.Text, nullable=False)
    intervention_date = db.Column(db.DateTime, default=datetime.utcnow)
    follow_up_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(50), default='Planned')          # Planned, In Progress, Completed, Cancelled
    outcome_notes = db.Column(db.Text, nullable=True)
