import json
from datetime import datetime
from app.extensions import db

class Resume(db.Model):
    """Resume database model representing uploaded CV files."""
    __tablename__ = 'resumes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)  # pdf, docx, txt
    file_size = db.Column(db.Integer, default=0)
    
    # Text contents and extraction status
    raw_text = db.Column(db.Text, nullable=True)
    parsed_data = db.Column(db.Text, nullable=True)  # Store JSON as string for compatibility across DB types
    status = db.Column(db.String(20), default='uploaded')  # uploaded, parsing, parsed, error
    
    # Timestamps
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    candidate_profile = db.relationship('CandidateProfile', backref='resume', uselist=False, cascade="all, delete-orphan")
    match_results = db.relationship('MatchResult', backref='resume', lazy=True, cascade="all, delete-orphan")

    @property
    def created_at(self):
        return self.upload_date

    def get_parsed_json(self):
        """Helper to get parsed_data as dictionary."""
        if self.parsed_data:
            try:
                return json.loads(self.parsed_data)
            except json.JSONDecodeError:
                return {}
        return {}

    def set_parsed_json(self, data):
        """Helper to set parsed_data from dictionary."""
        self.parsed_data = json.dumps(data)

    @property
    def file_path(self):
        import os
        from flask import current_app
        return os.path.join(current_app.config['UPLOAD_FOLDER'], self.filename)

    @property
    def candidate_name(self):
        return self.candidate_profile.name if self.candidate_profile else None

    @property
    def parsed_email(self):
        return self.candidate_profile.email if self.candidate_profile else None

    @property
    def parsed_phone(self):
        return self.candidate_profile.phone if self.candidate_profile else None

    @property
    def skills(self):
        return self.candidate_profile.skills_list if self.candidate_profile else []

    @property
    def experience_years(self):
        return self.candidate_profile.total_experience_years if self.candidate_profile else 0.0

    @property
    def education_level(self):
        if self.candidate_profile and self.candidate_profile.education_list:
            edu = self.candidate_profile.education_list[0]
            if isinstance(edu, dict):
                return edu.get('degree', '')
            return str(edu)
        return ''

    def to_dict(self):
        """Convert object fields into dictionary for API usage."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'status': self.status,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'has_profile': self.candidate_profile is not None
        }

    def __repr__(self):
        return f"<Resume {self.original_filename} (Status: {self.status})>"


class CandidateProfile(db.Model):
    """Candidate profile model representing the parsed, structured candidate data."""
    __tablename__ = 'candidate_profiles'

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id', ondelete='CASCADE'), nullable=False, unique=True)
    
    # Extracted fields
    name = db.Column(db.String(150))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(30))
    location = db.Column(db.String(150))
    summary = db.Column(db.Text)
    
    # Structured fields stored as serialized JSON strings for PostgreSQL compatibility
    skills = db.Column(db.Text)         # JSON list: ["Python", "SQL", ...]
    education = db.Column(db.Text)      # JSON list of dicts: [{"degree": "...", "institution": "...", ...}]
    experience = db.Column(db.Text)     # JSON list of dicts: [{"role": "...", "company": "...", ...}]
    certifications = db.Column(db.Text) # JSON list: ["AWS Cloud Practitioner", ...]
    projects = db.Column(db.Text)       # JSON list of dicts: [{"title": "...", "tech_stack": [...], ...}]
    links = db.Column(db.Text)          # JSON dict: {"linkedin": "...", "github": "..."}
    languages = db.Column(db.Text)      # JSON list: ["English", "German"]
    
    total_experience_years = db.Column(db.Float, default=0.0)

    # JSON helper getters/setters
    def _get_json_field(self, field_name, default=[]):
        val = getattr(self, field_name)
        if val:
            try:
                return json.loads(val)
            except json.JSONDecodeError:
                return default
        return default

    def _set_json_field(self, field_name, value):
        setattr(self, field_name, json.dumps(value))

    @property
    def skills_list(self): return self._get_json_field('skills', [])
    @skills_list.setter
    def skills_list(self, val): self._set_json_field('skills', val)

    @property
    def education_list(self): return self._get_json_field('education', [])
    @education_list.setter
    def education_list(self, val): self._set_json_field('education', val)

    @property
    def experience_list(self): return self._get_json_field('experience', [])
    @experience_list.setter
    def experience_list(self, val): self._set_json_field('experience', val)

    @property
    def certifications_list(self): return self._get_json_field('certifications', [])
    @certifications_list.setter
    def certifications_list(self, val): self._set_json_field('certifications', val)

    @property
    def projects_list(self): return self._get_json_field('projects', [])
    @projects_list.setter
    def projects_list(self, val): self._set_json_field('projects', val)

    @property
    def links_dict(self): return self._get_json_field('links', {})
    @links_dict.setter
    def links_dict(self, val): self._set_json_field('links', val)

    @property
    def languages_list(self): return self._get_json_field('languages', [])
    @languages_list.setter
    def languages_list(self, val): self._set_json_field('languages', val)

    def to_dict(self):
        """Convert object fields into dictionary for API usage."""
        return {
            'id': self.id,
            'resume_id': self.resume_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'location': self.location,
            'summary': self.summary,
            'skills': self.skills_list,
            'education': self.education_list,
            'experience': self.experience_list,
            'certifications': self.certifications_list,
            'projects': self.projects_list,
            'links': self.links_dict,
            'languages': self.languages_list,
            'total_experience_years': self.total_experience_years
        }

    def __repr__(self):
        return f"<CandidateProfile {self.name or 'Unknown'}>"
