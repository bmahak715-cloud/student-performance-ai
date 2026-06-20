import os
from flask import Flask, render_template

from config import Config
from utils.database import db
from utils.helpers import format_datetime, get_risk_badge_class, get_risk_percentage, parse_json_safely

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize SQLAlchemy database instance
    db.init_app(app)
    
    # Register helper filters in Jinja templates
    app.jinja_env.filters['datetime'] = format_datetime
    app.jinja_env.filters['risk_badge'] = get_risk_badge_class
    app.jinja_env.filters['risk_pct'] = get_risk_percentage
    app.jinja_env.filters['json_parse'] = parse_json_safely
    
    # Register Blueprints
    from routes.auth_routes import auth_bp
    from routes.dashboard_routes import dashboard_bp
    from routes.student_routes import student_bp
    from routes.prediction_routes import prediction_bp
    from routes.intervention_routes import intervention_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(prediction_bp)
    app.register_blueprint(intervention_bp)
    
    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
        
    @app.errorhandler(500)
    def internal_server_error(e):
        # Do not expose internal details/stack traces to users
        return render_template('500.html'), 500
        
    # Ensure all database tables are created on startup
    # This is safe to call multiple times — SQLAlchemy only creates tables that don't exist yet
    with app.app_context():
        db.create_all()
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
