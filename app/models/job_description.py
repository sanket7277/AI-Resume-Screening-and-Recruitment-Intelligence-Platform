import json
from datetime import datetime
from app.extensions import db

class JobDescription(db.Model):
    """JobDescription database model representing recruiter postings."""
    __tablename__ = 'job_descriptions'

    id = db.Column(db.Integer, primary_key=True)
    recruiter_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(150), nullable=False)
    department = db.Column(db.String(100))
    location = db.Column(db.String(150))
    
    # Description texts
    description = db.Column(db.Text, nullable=False)
    responsibilities = db.Column(db.Text)
    
    # Structured fields stored as JSON arrays natively
    required_skills = db.Column(db.JSON, default=list)    # JSON list of strings
    preferred_skills = db.Column(db.JSON, default=list)   # JSON list of strings
    
    # Filters/Requirements
    min_experience = db.Column(db.Integer, default=0)
    max_experience = db.Column(db.Integer)
    education_level = db.Column(db.String(100))  # e.g., Bachelors, Masters, PhD, any
    requirements = db.Column(db.Text)
    employment_type = db.Column(db.String(50), default='full-time')  # full-time, part-time, contract, internship
    
    # Salary Range
    salary_min = db.Column(db.Integer)
    salary_max = db.Column(db.Integer)
    
    is_active = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(20), default='active')  # draft, active, closed
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    match_results = db.relationship('MatchResult', backref='job', lazy=True, cascade="all, delete-orphan")



    @property
    def created_by(self):
        return self.recruiter_id

    @created_by.setter
    def created_by(self, val):
        self.recruiter_id = val

    @property
    def education_required(self):
        return self.education_level

    @education_required.setter
    def education_required(self, val):
        self.education_level = val

    def get_all_skills(self):
        """Combine required and preferred skills lists."""
        req = self.required_skills if self.required_skills else []
        pref = self.preferred_skills if self.preferred_skills else []
        return list(set(req + pref))

    def to_dict(self):
        """Convert object fields into dictionary for API usage."""
        return {
            'id': self.id,
            'recruiter_id': self.recruiter_id,
            'title': self.title,
            'company': self.company,
            'department': self.department,
            'location': self.location,
            'description': self.description,
            'responsibilities': self.responsibilities,
            'required_skills': self.required_skills if self.required_skills else [],
            'preferred_skills': self.preferred_skills if self.preferred_skills else [],
            'min_experience': self.min_experience,
            'max_experience': self.max_experience,
            'education_level': self.education_level,
            'employment_type': self.employment_type,
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'is_active': self.is_active,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<JobDescription {self.title} at {self.company}>"
