import os
import random
from datetime import datetime, timedelta
from app import create_app
from utils.database import db, Educator, Student, AcademicRecord, Attendance, LMSEngagement, Intervention
from services.prediction_service import generate_and_save_prediction

def seed_database():
    app = create_app()
    with app.app_context():
        # Create database and all tables
        db.create_all()
        print("Database tables created successfully.")
        
        # 1. Seed Educator
        educator = Educator.query.filter_by(email="educator@college.edu").first()
        if not educator:
            educator = Educator(
                name="Dr. Sarah Jenkins",
                email="educator@college.edu"
            )
            educator.set_password("Password123")
            db.session.add(educator)
            db.session.commit()
            print("Default educator account created:")
            print("  Email: educator@college.edu")
            print("  Password: Password123")
        else:
            print("Educator account already exists.")
            
        # Check if students exist
        if Student.query.count() > 0:
            print("Database already seeded with student records. Skipping student seed.")
            return
            
        print("Seeding sample student records...")
        
        # 2. Student definitions: Name, age, course, sem, sec, prev_gpa, and risk profiles
        student_configs = [
            # High Performing, low risk
            {
                'student_id': 'STU2041', 'name': 'Riya Sharma', 'age': 20, 
                'course': 'B.Sc Computer Science', 'semester': 4, 'section': 'A', 'previous_gpa': 3.75,
                'attendance': [90, 92, 95], 'assignments': [88, 92, 94], 'quizzes': [85, 90, 92],
                'midterm': 88, 'practical': 92, 'project': 95, 'prev_res': 90,
                'lms_logins': [10, 12, 14], 'lms_hours': [15, 18, 20], 'discussion': 8, 'materials': 80
            },
            # High Risk student (failing marks, low attendance)
            {
                'student_id': 'STU2078', 'name': 'Aman Khan', 'age': 21, 
                'course': 'B.Sc Computer Science', 'semester': 4, 'section': 'A', 'previous_gpa': 2.10,
                'attendance': [62, 58, 55], 'assignments': [45, 40, 38], 'quizzes': [50, 42, 40],
                'midterm': 44, 'practical': 50, 'project': 45, 'prev_res': 55,
                'lms_logins': [3, 2, 1], 'lms_hours': [4, 3, 2], 'discussion': 0, 'materials': 15,
                'consec_abs': 6, 'late_arr': 4
            },
            # Medium Risk student (declining attendance, average scores)
            {
                'student_id': 'STU2103', 'name': 'Priya Verma', 'age': 19, 
                'course': 'B.Sc Computer Science', 'semester': 4, 'section': 'A', 'previous_gpa': 2.95,
                'attendance': [80, 75, 72], 'assignments': [65, 60, 58], 'quizzes': [70, 64, 60],
                'midterm': 52, 'practical': 65, 'project': 70, 'prev_res': 72,
                'lms_logins': [6, 5, 4], 'lms_hours': [8, 7, 6], 'discussion': 2, 'materials': 45,
                'consec_abs': 3, 'late_arr': 2
            },
            # Low Risk student (stable middle performance)
            {
                'student_id': 'STU2119', 'name': 'Sara Nair', 'age': 20, 
                'course': 'B.Sc Computer Science', 'semester': 4, 'section': 'A', 'previous_gpa': 3.10,
                'attendance': [88, 89, 89], 'assignments': [74, 76, 75], 'quizzes': [72, 75, 74],
                'midterm': 74, 'practical': 78, 'project': 80, 'prev_res': 75,
                'lms_logins': [8, 8, 9], 'lms_hours': [11, 12, 12], 'discussion': 4, 'materials': 60
            },
            # Borderline Medium/High Risk
            {
                'student_id': 'STU2130', 'name': 'John Doe', 'age': 22, 
                'course': 'B.Sc Computer Science', 'semester': 4, 'section': 'B', 'previous_gpa': 2.45,
                'attendance': [70, 68, 65], 'assignments': [58, 55, 52], 'quizzes': [55, 50, 48],
                'midterm': 46, 'practical': 58, 'project': 60, 'prev_res': 50,
                'lms_logins': [4, 3, 3], 'lms_hours': [5, 4, 4], 'discussion': 1, 'materials': 25,
                'consec_abs': 4, 'late_arr': 3
            }
        ]
        
        # We will loop and add student history going back 3 weeks to generate nice charts
        base_date = datetime.utcnow()
        
        for config in student_configs:
            # 1. Create Student metadata
            student = Student(
                student_id=config['student_id'],
                name=config['name'],
                age=config['age'],
                course=config['course'],
                semester=config['semester'],
                section=config['section'],
                previous_gpa=config['previous_gpa'],
                created_at=base_date - timedelta(days=25)
            )
            db.session.add(student)
            db.session.commit()
            
            # 2. Add multiple weekly logs to create historical timelines
            for week_idx in range(3):
                log_date = base_date - timedelta(days=21 - (week_idx * 7))
                
                # Fetch mock weekly values
                att_val = config['attendance'][week_idx]
                assign_val = config['assignments'][week_idx]
                quiz_val = config['quizzes'][week_idx]
                logins = config['lms_logins'][week_idx]
                hours = config['lms_hours'][week_idx]
                
                # Create Academic Record
                acad = AcademicRecord(
                    student_id=student.id,
                    assignment_average=float(assign_val),
                    quiz_average=float(quiz_val),
                    midterm_marks=float(config['midterm']),
                    practical_marks=float(config['practical']),
                    project_marks=float(config['project']),
                    previous_result=float(config['prev_res']),
                    record_date=log_date
                )
                
                # Create Attendance Log
                total_cls = 10 + (week_idx * 5)
                attended_cls = int(round((att_val / 100) * total_cls))
                att_pct = (attended_cls / total_cls) * 100
                
                att = Attendance(
                    student_id=student.id,
                    total_classes=total_cls,
                    attended_classes=attended_cls,
                    attendance_percentage=att_pct,
                    consecutive_absences=config.get('consec_abs', 0) if week_idx == 2 else max(0, config.get('consec_abs', 0)-2),
                    late_arrivals=config.get('late_arr', 0) if week_idx == 2 else max(0, config.get('late_arr', 0)-1),
                    record_date=log_date
                )
                
                # Create LMS Engagement
                lms = LMSEngagement(
                    student_id=student.id,
                    login_frequency=logins,
                    materials_accessed=int(round((config['materials'] / 3) * (week_idx + 1))),
                    quiz_attempts=2 + week_idx if quiz_val > 60 else 1,
                    assignments_submitted=int(round((assign_val / 100) * 5)),
                    total_assignments=5,
                    late_submissions=1 if week_idx == 1 and config['previous_gpa'] < 2.5 else 0,
                    time_spent=float(hours),
                    discussion_participation=int(round((config['discussion'] / 3) * (week_idx + 1))),
                    record_date=log_date
                )
                
                db.session.add(acad)
                db.session.add(att)
                db.session.add(lms)
                db.session.commit()
            
            # 3. Generate ML Prediction history records for each historical log
            # We run predictions to ensure timeline and comparison data exist in the DB!
            try:
                # Run prediction for latest state
                generate_and_save_prediction(student.id)
            except Exception as ex:
                print(f"  Note: ML prediction auto-generation failed for {student.name} ({ex}).")
                print("  This is normal if ML models are not yet trained. Run train_model.py to enable ML features.")
                
            # 4. Add a sample Intervention for at-risk students
            if config['previous_gpa'] < 2.5: # Aman Khan / John Doe
                intervention = Intervention(
                    student_id=student.id,
                    educator_id=educator.id,
                    intervention_type="Academic counselling" if config['previous_gpa'] > 2.2 else "Attendance support",
                    description="Scheduled counseling session to discuss attendance gaps and midterm marks.",
                    intervention_date=datetime.utcnow() - timedelta(days=2),
                    follow_up_date=datetime.utcnow() + timedelta(days=10),
                    status="In Progress",
                    outcome_notes="Student attended initial counseling; agreed to sign weekly attendance review sheets."
                )
                db.session.add(intervention)
                db.session.commit()
                
        print("Database seeded successfully with sample student logs and historical predictions.")

if __name__ == '__main__':
    seed_database()
