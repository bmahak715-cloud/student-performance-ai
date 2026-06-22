# Predicting Student Performance Using AI for Early Academic Intervention
Live: https://student-performance-ai-3pry.onrender.com/

A comprehensive, production-ready student performance prediction and early academic intervention system designed to support educators in academic institutions. The system uses machine learning regression to predict final marks and classification models to identify students at risk of academic underperformance, highlighting key risk factors and recommending constructive support plans.

---

## 1. Introduction & Objectives

### Problem Statement
In higher education, identifying students who are struggling with course materials, irregular class attendance, or low digital learning engagement is often realized too late. Traditional assessments occur after key topics are taught, missing the window for early, effective academic intervention.

### Project Objectives
- **Early Classification:** Quantify and categorize student academic risk (Low, Medium, High) early in the semester.
- **Marks Projection:** Estimate expected final course grades to enable proactive mentoring.
- **Explainability (Responsible AI):** Decode model predictions to isolate increasing and reducing factors in plain language.
- **Intervention Lifecycle Tracking:** Streamline planning, assignment, and status updates of support plans (tutoring, counselling, study plans).
- **Security & Data Safety:** Build a secure educator-only interface preventing demographic bias by training models solely on academic engagement indicators.

---

## 2. Features

- **Aggregated Analytics Dashboard:** Track institutional counts (total students, risk breakdowns, average attendance, predicted marks) alongside interactive distribution donut and line charts.
- **Interactive Student Profiles:** View student historical marks, attendance percentages, and digital LMS activity logs alongside local feature importances and historical prediction trajectories.
- **Intelligent Explanation Engine:** Translate ML feature importances into readable summaries using structured rules, with optional Gemini GenAI API integration for advanced writeups.
- **Custom Intervention Registry:** Log tutor assignments, attendance review plans, and counsel sessions with follow-up date flags and outcome summaries.
- **Real-Time REST APIs:** Direct JSON endpoints for model inference (`/api/predict`), student lookup, and history logs.
- **Bias Auditing (Fairness Audit):** Assess model accuracy, false-positive, and false-negative ratios across semesters or age brackets to ensure model transparency.

---

## 3. Technology Stack

- **Backend Logic:** Python 3.9+, Flask (Application Factory), Blueprint-based routes
- **Database Layer:** SQLite, Flask-SQLAlchemy (Parameterized Query Security)
- **Machine Learning:** Pandas, NumPy, Scikit-learn, Joblib
- **Visualization:** Chart.js, HTML, CSS (Custom Dark Glassmorphic Theme), Bootstrap 5
- **Testing:** Pytest

---

## 4. Folder Structure

```text
student-performance-system/
│
├── app.py                      # Flask Application Factory setup
├── config.py                   # App configurations and constants
├── requirements.txt            # Python environment packages list
├── README.md                   # Project documentation
├── .env                        # Active environment keys
├── .env.example                # Configuration template
├── seed_db.py                  # Database initial seeding script
│
├── database/
│   └── student_performance.db  # Active SQLite database file
│
├── datasets/
│   └── student_data.csv        # Simulated student training dataset
│
├── models/
│   ├── risk_model.pkl          # Trained Classification model (at-risk)
│   ├── marks_model.pkl         # Trained Regression model (marks)
│   ├── preprocessing_pipeline.pkl  # Imputation & Scaling pipeline
│   ├── feature_names.pkl       # Input columns list
│   └── evaluation_results.json # Saved model performance report
│
├── ml/
│   ├── generate_dataset.py     # Synthetic data generator
│   ├── preprocess.py           # Preprocessing pipeline setup
│   ├── feature_engineering.py   # Engineered column calculations
│   ├── train_model.py          # Model training orchestrator
│   ├── evaluate_model.py       # Metrics & subgroup fairness audit
│   ├── predict.py              # Single profile inference wrappers
│   └── explain.py              # Local attribution details generator
│
├── routes/
│   ├── auth_routes.py          # Educator registration & login controllers
│   ├── dashboard_routes.py     # Aggregated stats & chart datasets routes
│   ├── student_routes.py       # Student CRUD & logs controller
│   ├── prediction_routes.py    # Trigger predictions & REST APIs
│   └── intervention_routes.py  # Support logging and update routes
│
├── services/
│   ├── prediction_service.py   # Database metrics extraction to ML bridge
│   ├── explanation_service.py  # Natural language translation layer
│   └── intervention_service.py # Targeted recommendations ruleset
│
├── templates/
│   ├── base.html               # Primary shell template (sidebar/navbar)
│   ├── login.html              # Educator login screen
│   ├── register.html           # Educator registration screen
│   ├── dashboard.html          # Main metrics panel and Chart.js canvases
│   ├── students.html           # Directory table with pagination & searches
│   ├── add_student.html        # Unified registration & baseline log form
│   ├── edit_student.html       # Profile edit form
│   ├── student_details.html    # Student tabs: AI, Academics, Attendance, Charts
│   ├── interventions.html      # Complete intervention registry log
│   ├── 404.html                # Not Found error page
│   └── 500.html                # Internal Server error page
│
├── static/
│   ├── css/
│   │   └── style.css           # Curated dark/glassmorphic stylesheet
│   └── js/
│       ├── dashboard.js        # Timestamps & alert auto-dismiss routines
│       └── charts.js           # Chart.js configs for donut, lines & trends
│
├── utils/
│   ├── database.py             # SQLAlchemy models definitions
│   ├── validators.py           # Custom form input validators
│   └── helpers.py              # Datetime filters & risk badge classes
│
└── tests/
    ├── conftest.py             # Pytest fixtures and mock database setup
    ├── test_auth.py            # Auth module tests
    ├── test_students.py        # Student logs tests
    ├── test_predictions.py     # ML & API routes tests
    └── test_interventions.py   # Interventions tracker tests
```

---

## 5. Installation & Execution (Windows Instructions)

Follow these steps in a command prompt or PowerShell terminal:

### Step 1: Clone or Place files in Workspace
Ensure the folder structure matches the directories above inside your project workspace.

### Step 2: Set Up Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Generate Simulated Student Dataset
```bash
python ml/generate_dataset.py
```
This writes 550 realistic student records into `datasets/student_data.csv`.

### Step 5: Train Machine Learning Models
```bash
python ml/train_model.py
```
This tests regression and classification models, saves the best ones to the `models/` directory, and writes evaluation performance reports to `models/evaluation_results.json`.

### Step 6: Initialize & Seed Database
```bash
python seed_db.py
```
This creates the SQLite database and adds a default educator account (`educator@college.edu` / `Password123`) and 5 sample students with historical records.

### Step 7: Run Flask Server
```bash
python app.py
```
Open a browser and navigate to: [http://127.0.0.1:5000](http://127.0.0.1:5000)

**Default Educator Credentials:**
- **Email:** `educator@college.edu`
- **Password:** `Password123`

---

## 6. REST API Documentation

### 1. Predict Performance Risk
- **Endpoint:** `POST /api/predict`
- **Content-Type:** `application/json`
- **Request Payload Example:**
```json
{
  "student_id": "STU8090",
  "name": "API Student",
  "age": 20,
  "course": "B.Sc Computer Science",
  "semester": 4,
  "section": "A",
  "previous_gpa": 3.20,
  "assignment_average": 55.5,
  "quiz_average": 50.0,
  "midterm_marks": 45.0,
  "practical_marks": 60.0,
  "project_marks": 50.0,
  "previous_result": 65.0,
  "total_classes": 15,
  "attended_classes": 10,
  "consecutive_absences": 4,
  "late_arrivals": 2,
  "login_frequency": 3,
  "materials_accessed": 10,
  "quiz_attempts": 1,
  "assignments_submitted": 3,
  "total_assignments": 5,
  "late_submissions": 2,
  "time_spent": 4.5,
  "discussion_participation": 0
}
```

- **Response Example (200 OK):**
```json
{
  "completion_probability": 31.6,
  "explanation": "The prediction indicates a High risk profile with an academic risk probability of 68.4% and an expected final grade of 52.3/100...",
  "important_features": {
    "increasing": [
      "Low attendance rate (66.7%)",
      "Poor average internal marks (56.1/100)",
      "Frequent consecutive absences (4 days)"
    ],
    "reducing": [
      "Strong prior academic foundation (GPA: 3.20)"
    ]
  },
  "model_version": "1.0.0",
  "predicted_marks": 52.3,
  "recommendations": [
    {
      "action": "Schedule a meeting with the student to identify barriers to class attendance...",
      "priority": "High",
      "reason": "Attendance is 66.7% with 4 consecutive absences.",
      "type": "Attendance support"
    }
  ],
  "risk_level": "High",
  "risk_probability": 0.684
}
```

### 2. Get Student Prediction History
- **Endpoint:** `GET /api/students/<student_id>/predictions`
- **Response Example (200 OK):**
```json
{
  "student_id": "STU2078",
  "student_name": "Aman Khan",
  "predictions": [
    {
      "prediction_id": 2,
      "predicted_marks": 46.2,
      "risk_probability": 0.784,
      "risk_level": "High",
      "completion_probability": 21.6,
      "explanation": "...",
      "prediction_date": "2026-06-20T15:40:00"
    }
  ]
}
```

### 3. Log Support Intervention
- **Endpoint:** `POST /api/students/<student_id>/interventions`
- **Content-Type:** `application/json`
- **Request Payload Example:**
```json
{
  "educator_email": "educator@college.edu",
  "intervention_type": "Subject tutoring",
  "description": "Weekly tutoring assigned with a student mentor for midterm recovery.",
  "follow_up_date": "2026-07-05",
  "status": "In Progress"
}
```

---

## 7. Testing Instructions

To execute the unit test suites:
```bash
pytest tests/
```
The test configurations utilize an in-memory SQLite database, verifying routing, sessions, form validations, database queries, and predictions without impacting your development database.

---

## 8. Responsible AI & Limitations

### Responsible AI Disclaimer
> [!WARNING]
> This prediction is intended to support educators and must not be used as the sole basis for academic, disciplinary, or administrative decisions.
>
> The system must always remain **human-in-the-loop**. The ML output is a statistical projection based on class engagement indicators and must never be treated as an absolute guarantee of student outcome, nor should it trigger automated disciplinary reviews.

### Limitations
- **Data Dependency:** The system assumes consistent logging of weekly assessment, attendance, and LMS metrics.
- **Historical Scope:** Real-time predictions reflect only current student inputs, without modeling long-term semester-over-semester behavioral trajectories.
