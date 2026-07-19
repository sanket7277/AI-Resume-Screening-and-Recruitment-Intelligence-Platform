import os
from flask import Flask, render_template
from config import config_by_name
from app.extensions import db, bcrypt, login_manager, migrate


def create_app(config_name='development'):
    """Application factory for setting up the Flask application."""
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['ML_MODEL_PATH'], exist_ok=True)

    # Register blueprints
    try:
        from app.blueprints.auth import auth_bp
        app.register_blueprint(auth_bp, url_prefix='/auth')
    except ImportError as e:
        app.logger.warning(f"Failed to load auth blueprint: {e}")

    try:
        from app.blueprints.main import main_bp
        app.register_blueprint(main_bp)
    except ImportError as e:
        app.logger.warning(f"Failed to load main blueprint: {e}")

    try:
        from app.blueprints.dashboard import dashboard_bp
        app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    except ImportError as e:
        app.logger.warning(f"Failed to load dashboard blueprint: {e}")

    try:
        from app.blueprints.resume import resume_bp
        app.register_blueprint(resume_bp, url_prefix='/resume')
    except ImportError as e:
        app.logger.warning(f"Failed to load resume blueprint: {e}")

    try:
        from app.blueprints.jobs import jobs_bp
        app.register_blueprint(jobs_bp, url_prefix='/jobs')
    except ImportError as e:
        app.logger.warning(f"Failed to load jobs blueprint: {e}")

    try:
        from app.blueprints.matching import matching_bp
        app.register_blueprint(matching_bp, url_prefix='/matching')
    except ImportError as e:
        app.logger.warning(f"Failed to load matching blueprint: {e}")

    try:
        from app.blueprints.analytics import analytics_bp
        app.register_blueprint(analytics_bp, url_prefix='/analytics')
    except ImportError as e:
        app.logger.warning(f"Failed to load analytics blueprint: {e}")

    try:
        from app.blueprints.admin import admin_bp
        app.register_blueprint(admin_bp, url_prefix='/admin')
    except ImportError as e:
        app.logger.warning(f"Failed to load admin blueprint: {e}")

    try:
        from app.blueprints.api import api_bp
        app.register_blueprint(api_bp, url_prefix='/api/v1')
    except ImportError as e:
        app.logger.warning(f"Failed to load api blueprint: {e}")

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    # Import all models so SQLAlchemy registers them
    from app.models.user import User
    from app.models.resume import Resume, CandidateProfile
    from app.models.job_description import JobDescription
    from app.models.match_result import MatchResult
    from app.models.skill import Skill
    from app.models.analytics import AnalyticsSnapshot

    # Create database tables automatically
    with app.app_context():
        db.create_all()

    return app