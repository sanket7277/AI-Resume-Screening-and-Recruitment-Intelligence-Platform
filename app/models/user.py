from datetime import datetime
from app.extensions import db, bcrypt
from flask_login import UserMixin

class User(UserMixin, db.Model):
    """User database model representing admins, recruiters, and candidates."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='candidate')  # 'admin', 'recruiter', 'candidate'
    
    # Profile & Business details
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    company = db.Column(db.String(120))  # recruiter specific
    phone = db.Column(db.String(20))
    avatar_url = db.Column(db.String(256))
    bio = db.Column(db.Text)
    department = db.Column(db.String(120))
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    resumes = db.relationship('Resume', backref='user', lazy=True, cascade="all, delete-orphan")
    job_descriptions = db.relationship('JobDescription', backref='recruiter', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        """Create bcrypt password hash."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Check bcrypt password hash."""
        return bcrypt.check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        """Check if user has admin privileges."""
        return self.role == 'admin'

    @property
    def is_recruiter(self):
        """Check if user has recruiter privileges."""
        return self.role in ['recruiter', 'admin']

    @property
    def is_candidate(self):
        """Check if user is a job seeker/candidate."""
        return self.role == 'candidate'

    @property
    def full_name(self):
        """Return user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.username

    def to_dict(self):
        """Convert object fields into dictionary for API usage."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'company': self.company,
            'phone': self.phone,
            'avatar_url': self.avatar_url,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"
