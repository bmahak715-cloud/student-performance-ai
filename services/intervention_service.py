def suggest_interventions(metrics, risk_level):
    """
    Formulate targeted academic intervention suggestions based on the student's
    underlying performance, attendance, and LMS metrics.
    """
    recommendations = []
    
    attendance = metrics.get('attendance_percentage', 100.0)
    quiz_avg = metrics.get('quiz_average', 100.0)
    assign_avg = metrics.get('assignment_average', 100.0)
    midterm = metrics.get('midterm_marks', 100.0)
    sub_rate = metrics.get('assignment_submission_rate', 1.0)
    late_rate = metrics.get('late_submission_rate', 0.0)
    lms_freq = metrics.get('login_frequency', 10)
    time_spent = metrics.get('time_spent', 20.0)
    consec_abs = metrics.get('consecutive_absences', 0)
    
    # 1. Attendance Intervention
    if attendance < 75 or consec_abs >= 3:
        recommendations.append({
            'type': 'Attendance support',
            'priority': 'High' if attendance < 65 or consec_abs >= 5 else 'Medium',
            'reason': f"Attendance is {attendance:.1f}% with {consec_abs} consecutive absences.",
            'action': "Schedule a meeting with the student to identify barriers to class attendance. Establish an attendance contract and connect them with student services if transportation or scheduling issues exist."
        })
        
    # 2. Assignment Recovery Plan
    if sub_rate < 0.85 or late_rate > 0.25:
        recommendations.append({
            'type': 'Assignment recovery plan',
            'priority': 'High' if sub_rate < 0.70 else 'Medium',
            'reason': f"Assignment completion is {sub_rate*100:.1f}% with {late_rate*100:.1f}% submitted late.",
            'action': "Identify missing coursework items. Draft a step-by-step submission schedule with partial credit recovery options to prevent cumulative zero grades."
        })
        
    # 3. Subject Tutoring
    if quiz_avg < 60 or assign_avg < 60:
        recommendations.append({
            'type': 'Subject tutoring',
            'priority': 'High' if (quiz_avg < 50 or assign_avg < 50) else 'Medium',
            'reason': f"Assignment average ({assign_avg:.1f}%) or Quiz average ({quiz_avg:.1f}%) is below 60%.",
            'action': "Refer the student to peer tutoring centers or department study halls. Focus on foundational lecture topics and weekly assignment reviews."
        })
        
    # 4. Remedial Classes
    if midterm < 50:
        recommendations.append({
            'type': 'Remedial classes',
            'priority': 'High' if midterm < 40 else 'Medium',
            'reason': f"Midterm exam score was low ({midterm:.1f}/100).",
            'action': "Invite the student to professor office hours or structured midterm review workshops. Go over exam mistakes and offer mock exam practice."
        })
        
    # 5. Study Planning
    if lms_freq < 3 or time_spent < 5.0:
        recommendations.append({
            'type': 'Study planning',
            'priority': 'Medium',
            'reason': f"LMS activity is low (weekly logins: {lms_freq}, study time: {time_spent:.1f} hrs).",
            'action': "Provide the student with a digital study guide. Walk them through self-paced learning objectives on the LMS and suggest weekly dashboard tracking goals."
        })
        
    # 6. Academic Counselling
    if risk_level == 'High' or (metrics.get('previous_gpa', 4.0) < 2.3 and risk_level == 'Medium'):
        recommendations.append({
            'type': 'Academic counselling',
            'priority': 'High',
            'reason': f"Student has a {risk_level} academic risk profile.",
            'action': "Arrange a formal academic advising session. Evaluate overall course load, study habits, external work commitments, and discuss potential course adjustment options."
        })
        
    # 7. Fallback generic recommendation if student is doing well but has minor variance
    if not recommendations:
        recommendations.append({
            'type': 'Peer mentoring',
            'priority': 'Low',
            'reason': "Low risk profile, general encouragement.",
            'action': "Assign a senior peer mentor to share study strategies and support high-grade maintenance throughout the semester."
        })
        
    # Always suggest a general follow-up meeting for at-risk cases
    if risk_level in ['Medium', 'High']:
        recommendations.append({
            'type': 'Follow-up meeting',
            'priority': 'Medium',
            'reason': "Scheduled risk review.",
            'action': "Set a follow-up date (within 10-14 days) to review progress on recommended study adjustments and attendance levels."
        })
        
    # Sort recommendations by priority (High, then Medium, then Low)
    priority_order = {'High': 0, 'Medium': 1, 'Low': 2}
    recommendations.sort(key=lambda x: priority_order.get(x['priority'], 3))
    
    return recommendations
