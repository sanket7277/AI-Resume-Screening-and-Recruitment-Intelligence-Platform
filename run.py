import os
from app import create_app, db
from flask_migrate import Migrate

# Get config name from environment, default to development
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    """Shell context for database debugging and manual tasks."""
    from app.models.user import User
    from app.models.resume import Resume, CandidateProfile
    from app.models.job_description import JobDescription
    from app.models.match_result import MatchResult
    from app.models.skill import Skill
    from app.models.analytics import AnalyticsSnapshot
    
    return {
        'db': db,
        'User': User,
        'Resume': Resume,
        'CandidateProfile': CandidateProfile,
        'JobDescription': JobDescription,
        'MatchResult': MatchResult,
        'Skill': Skill,
        'AnalyticsSnapshot': AnalyticsSnapshot
    }

if __name__ == '__main__':
    # Listen on all interfaces for Docker compatibility (standard student deployment practice)
    app.run(host='0.0.0.0', port=5000)
