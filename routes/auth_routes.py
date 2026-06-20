from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from utils.database import db, Educator
from utils.validators import validate_email, validate_password

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    """Decorator to protect private routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'educator_id' not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Educator registration route."""
    if 'educator_id' in session:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        errors = []
        if not name:
            errors.append("Name is required.")
        if not validate_email(email):
            errors.append("A valid email address is required.")
        if not validate_password(password):
            errors.append("Password must be at least 6 characters long.")
            
        # Check for duplicates
        existing = Educator.query.filter_by(email=email).first()
        if existing:
            errors.append("An educator account with this email already exists.")
            
        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template('register.html', name=name, email=email)
            
        # Create and save educator
        new_educator = Educator(name=name, email=email)
        new_educator.set_password(password)
        
        try:
            db.session.add(new_educator)
            db.session.commit()
            flash("Account registered successfully! Please log in.", "success")
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred during registration. Please try again.", "danger")
            
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Educator login route."""
    if 'educator_id' in session:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        next_url = request.form.get('next') or request.args.get('next')
        
        if not email or not password:
            flash("Please fill in all fields.", "danger")
            return render_template('login.html', email=email)
            
        educator = Educator.query.filter_by(email=email).first()
        
        if educator and educator.check_password(password):
            # Establish session credentials
            session['educator_id'] = educator.id
            session['educator_name'] = educator.name
            session['educator_email'] = educator.email
            
            flash(f"Welcome back, {educator.name}!", "success")
            if next_url:
                return redirect(next_url)
            return redirect(url_for('dashboard.index'))
        else:
            flash("Invalid email or password.", "danger")
            return render_template('login.html', email=email)
            
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    """Log out the educator."""
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('auth.login'))
