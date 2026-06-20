import pytest
from utils.database import db, Student, Intervention, Educator

def test_intervention_creation_and_update(client, app, seeded_educator):
    """Test adding an intervention and updating its status/outcome notes."""
    # Seed student
    with app.app_context():
        student = Student(student_id='STU3333', name='Carey Student', age=20, course='CS', semester=2, section='A', previous_gpa=2.2)
        db.session.add(student)
        db.session.commit()
        student_id = student.id
        
    with client.session_transaction() as sess:
        sess['educator_id'] = seeded_educator.id
        sess['educator_name'] = seeded_educator.name
        
    # 1. Add intervention
    response = client.post(f'/students/{student_id}/interventions/add', data={
        'intervention_type': 'Subject tutoring',
        'description': 'Tutoring for quiz recovery.',
        'follow_up_date': '2026-07-01'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Intervention successfully registered" in response.data
    
    with app.app_context():
        i_record = Intervention.query.filter_by(student_id=student_id).first()
        assert i_record is not None
        assert i_record.intervention_type == 'Subject tutoring'
        assert i_record.status == 'Planned'
        i_id = i_record.id
        
    # 2. Update status & outcome
    update_resp = client.post(f'/interventions/{i_id}/update', data={
        'status': 'Completed',
        'outcome_notes': 'Tutoring completed successfully. Grade improved.'
    }, follow_redirects=True)
    
    assert update_resp.status_code == 200
    assert b"Intervention status updated successfully" in update_resp.data
    
    with app.app_context():
        updated_i = Intervention.query.get(i_id)
        assert updated_i.status == 'Completed'
        assert updated_i.outcome_notes == 'Tutoring completed successfully. Grade improved.'
