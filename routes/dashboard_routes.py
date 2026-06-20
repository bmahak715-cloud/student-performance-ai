import json
from datetime import datetime
from flask import Blueprint, render_template, session, redirect, url_for
from routes.auth_routes import login_required
from utils.database import db, Student, AcademicRecord, Attendance, Prediction, Intervention, LMSEngagement

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    """Educator dashboard homepage rendering metrics, watchlists, and chart metadata."""
    students = Student.query.all()
    total_students = len(students)
    
    # Initialize trackers
    low_risk = 0
    med_risk = 0
    high_risk = 0
    total_attendance_pct = 0.0
    students_with_attendance = 0
    total_predicted_marks = 0.0
    students_with_predictions = 0
    
    recently_analyzed = []
    watchlist_high_risk = []
    risk_increased_list = []
    
    # Process student metrics
    for student in students:
        # Get latest attendance
        latest_att = Attendance.query.filter_by(student_id=student.id).order_by(Attendance.record_date.desc()).first()
        if latest_att:
            total_attendance_pct += latest_att.attendance_percentage
            students_with_attendance += 1
            
        # Get latest prediction
        latest_pred = Prediction.query.filter_by(student_id=student.id).order_by(Prediction.prediction_date.desc()).first()
        if latest_pred:
            students_with_predictions += 1
            total_predicted_marks += latest_pred.predicted_marks
            
            # Risk count
            r_level = latest_pred.risk_level.strip().lower()
            if r_level == 'high':
                high_risk += 1
                watchlist_high_risk.append((student, latest_pred, latest_att))
            elif r_level == 'medium':
                med_risk += 1
            else:
                low_risk += 1
                
            recently_analyzed.append((student, latest_pred, latest_att))
            
            # Risk increased check (fetch last two predictions)
            preds = Prediction.query.filter_by(student_id=student.id).order_by(Prediction.prediction_date.desc()).limit(2).all()
            if len(preds) == 2:
                latest_prob = preds[0].risk_probability
                prev_prob = preds[1].risk_probability
                if latest_prob > prev_prob + 0.05: # risk probability increased by more than 5%
                    risk_increased_list.append({
                        'student': student,
                        'latest_pred': preds[0],
                        'prev_pred': preds[1],
                        'increase': (latest_prob - prev_prob) * 100
                    })
                    
    # Formatting aggregations
    avg_attendance = (total_attendance_pct / students_with_attendance) if students_with_attendance > 0 else 0.0
    avg_predicted_marks = (total_predicted_marks / students_with_predictions) if students_with_predictions > 0 else 0.0
    
    # Interventions metrics
    pending_followups = Intervention.query.filter(Intervention.status.in_(['Planned', 'In Progress'])).all()
    pending_count = len(pending_followups)
    
    # Sort recently analyzed by prediction date desc
    recently_analyzed.sort(key=lambda x: x[1].prediction_date, reverse=True)
    recently_analyzed = recently_analyzed[:5]
    
    # Sort high risk watchlist by risk probability desc
    watchlist_high_risk.sort(key=lambda x: x[1].risk_probability, reverse=True)
    
    # Upcoming interventions follow-ups
    upcoming_followups = [
        item for item in pending_followups 
        if item.follow_up_date is not None
    ]
    upcoming_followups.sort(key=lambda x: x.follow_up_date)
    upcoming_followups = upcoming_followups[:5]
    
    # Chart 1: Risk Levels distribution counts
    risk_chart_data = {
        'labels': ['Low Risk', 'Medium Risk', 'High Risk'],
        'counts': [low_risk, med_risk, high_risk]
    }
    
    # Chart 2: Attendance Distribution
    att_ranges = {'< 60%': 0, '60% - 75%': 0, '75% - 90%': 0, '90%+': 0}
    # Chart 3: Predicted Marks Distribution
    marks_ranges = {'Fail (< 50)': 0, 'Pass (50 - 65)': 0, 'Merit (65 - 80)': 0, 'Distinction (80+)': 0}
    
    for student in students:
        latest_att = Attendance.query.filter_by(student_id=student.id).order_by(Attendance.record_date.desc()).first()
        if latest_att:
            val = latest_att.attendance_percentage
            if val < 60: att_ranges['< 60%'] += 1
            elif val < 75: att_ranges['60% - 75%'] += 1
            elif val < 90: att_ranges['75% - 90%'] += 1
            else: att_ranges['90%+'] += 1
            
        latest_pred = Prediction.query.filter_by(student_id=student.id).order_by(Prediction.prediction_date.desc()).first()
        if latest_pred:
            val = latest_pred.predicted_marks
            if val < 50: marks_ranges['Fail (< 50)'] += 1
            elif val < 65: marks_ranges['Pass (50 - 65)'] += 1
            elif val < 80: marks_ranges['Merit (65 - 80)'] += 1
            else: marks_ranges['Distinction (80+)'] += 1
            
    # Chart 4: Class Performance Trend (Aggregations over timeline Weeks)
    # We query the average attendance vs predicted marks from the database logs grouping by week.
    # For a prototype, we can build a 6-week trend based on the seeded database dates.
    class_trends = []
    # Fetch all records to compile weekly stats
    all_attendance = Attendance.query.all()
    # Mocking timeline weeks: group by record date's ISO week
    weekly_stats = {}
    for att_record in all_attendance:
        date_str = att_record.record_date.strftime("Wk %W")
        if date_str not in weekly_stats:
            weekly_stats[date_str] = {'att_sum': 0.0, 'att_cnt': 0, 'marks_sum': 0.0, 'marks_cnt': 0}
        weekly_stats[date_str]['att_sum'] += att_record.attendance_percentage
        weekly_stats[date_str]['att_cnt'] += 1
        
    all_predictions = Prediction.query.all()
    for pred_record in all_predictions:
        date_str = pred_record.prediction_date.strftime("Wk %W")
        if date_str in weekly_stats:
            weekly_stats[date_str]['marks_sum'] += pred_record.predicted_marks
            weekly_stats[date_str]['marks_cnt'] += 1
            
    # Formulate trend values
    sorted_weeks = sorted(weekly_stats.keys())
    trend_labels = []
    trend_attendance = []
    trend_marks = []
    for wk in sorted_weeks:
        stats = weekly_stats[wk]
        trend_labels.append(wk)
        trend_attendance.append(round(stats['att_sum'] / stats['att_cnt'], 1) if stats['att_cnt'] > 0 else 0)
        # Fallback marks to maintain scale on seed
        avg_m = stats['marks_sum'] / stats['marks_cnt'] if stats['marks_cnt'] > 0 else 65.0
        trend_marks.append(round(avg_m, 1))
        
    class_trend_data = {
        'labels': trend_labels[-6:] if len(trend_labels) > 0 else ["Wk1", "Wk2", "Wk3", "Wk4", "Wk5", "Wk6"],
        'attendance': trend_attendance[-6:] if len(trend_attendance) > 0 else [82, 80, 78, 75, 74, 73],
        'marks': trend_marks[-6:] if len(trend_marks) > 0 else [68, 66, 64, 62, 61, 60]
    }
    
    return render_template(
        'dashboard.html',
        total_students=total_students,
        low_risk=low_risk,
        med_risk=med_risk,
        high_risk=high_risk,
        avg_attendance=round(avg_attendance, 1),
        avg_predicted_marks=round(avg_predicted_marks, 1),
        pending_count=pending_count,
        recently_analyzed=recently_analyzed,
        watchlist_high_risk=watchlist_high_risk,
        risk_increased=risk_increased_list,
        upcoming_followups=upcoming_followups,
        risk_chart_data=json.dumps(risk_chart_data),
        attendance_chart_data=json.dumps({
            'labels': list(att_ranges.keys()),
            'counts': list(att_ranges.values())
        }),
        marks_chart_data=json.dumps({
            'labels': list(marks_ranges.keys()),
            'counts': list(marks_ranges.values())
        }),
        class_trend_data=json.dumps(class_trend_data)
    )
