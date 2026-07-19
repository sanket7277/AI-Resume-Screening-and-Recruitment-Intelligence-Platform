import os
from dotenv import load_dotenv

# Load variables from .env file if present
load_dotenv()

class Config:
    """Base configuration settings."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'recruitiq-super-secret-key-student-project'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload folder configuration
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB maximum upload size
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
    
    # ML Models path
    ML_MODEL_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app', 'ml', 'models')
    
    # NLP Model configuration
    SPACY_MODEL = 'en_core_web_sm'
    SBERT_MODEL = 'all-MiniLM-L6-v2'

class DevelopmentConfig(Config):
    """Development configuration settings."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///recruitment.db'

class ProductionConfig(Config):
    """Production configuration settings."""
    DEBUG = False

    # Use Render DATABASE_URL if available, otherwise use SQLite
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL")
        or "sqlite:///recruitment.db"
    )

    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True

class TestingConfig(Config):
    """Testing configuration settings."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
