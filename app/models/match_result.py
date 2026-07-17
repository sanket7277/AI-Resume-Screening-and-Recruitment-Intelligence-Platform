import json
from datetime import datetime
from app.extensions import db

class MatchResult(db.Model):
    """MatchResult database model representing ATS screening runs and suitability predictions."""
    __tablename__ = 'match_results'

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id', ondelete='CASCADE'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job_descriptions.id', ondelete='CASCADE'), nullable=False)
    
    # Matches scoring (out of 100)
    overall_score = db.Column(db.Float, default=0.0)      # primary weighted composite score
    skill_match_pct = db.Column(db.Float, default=0.0)
    education_match = db.Column(db.Float, default=0.0)    # binary or multi-value mapped to scale
    experience_match = db.Column(db.Float, default=0.0)   # comparison of years experience
    ats_score = db.Column(db.Float, default=0.0)          # alias kept for backwards compat
    keyword_coverage = db.Column(db.Float, default=0.0)   # TF-IDF keyword match percentage
    recommendation = db.Column(db.Text)                   # free-text AI recommendation

    # Detailed differences stored as serialized JSON strings
    matched_skills = db.Column(db.Text)      # JSON list of matched skill strings
    missing_skills = db.Column(db.Text)      # JSON list of strings
    extra_skills = db.Column(db.Text)        # JSON list of strings
    recommended_skills = db.Column(db.Text)  # JSON list of strings
    
    # NLP & Semantic Similarity Measures
    semantic_similarity = db.Column(db.Float, default=0.0)
    tfidf_similarity = db.Column(db.Float, default=0.0)
    cosine_similarity = db.Column(db.Float, default=0.0)
    
    # Ranking
    overall_rank = db.Column(db.Integer)
    
    # ML Classifications
    prediction_label = db.Column(db.String(50))        # Highly Suitable, Suitable, Average, Not Suitable
    prediction_confidence = db.Column(db.Float, default=0.0)
    
    # AI Explainability (JSON strings)
    strengths = db.Column(db.Text)            # JSON list of reasons
    weaknesses = db.Column(db.Text)           # JSON list of reasons
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Unique Constraint to prevent duplicate candidate matches for the same job description
    __table_args__ = (db.UniqueConstraint('resume_id', 'job_id', name='uq_resume_job_match'),)

    def _get_json_field(self, field_name):
        val = getattr(self, field_name)
        if val:
            try:
                return json.loads(val)
            except json.JSONDecodeError:
                return []
        return []

    def _set_json_field(self, field_name, value):
        setattr(self, field_name, json.dumps(value))

    # --- Python list-typed property accessors ---

    @property
    def matched_skills_list(self): return self._get_json_field('matched_skills')
    @matched_skills_list.setter
    def matched_skills_list(self, val): self._set_json_field('matched_skills', val)

    @property
    def missing_skills_list(self): return self._get_json_field('missing_skills')
    @missing_skills_list.setter
    def missing_skills_list(self, val): self._set_json_field('missing_skills', val)

    @property
    def extra_skills_list(self): return self._get_json_field('extra_skills')
    @extra_skills_list.setter
    def extra_skills_list(self, val): self._set_json_field('extra_skills', val)


    @property
    def recommended_skills_list(self): return self._get_json_field('recommended_skills')
    @recommended_skills_list.setter
    def recommended_skills_list(self, val): self._set_json_field('recommended_skills', val)

    @property
    def strengths_list(self): return self._get_json_field('strengths')
    @strengths_list.setter
    def strengths_list(self, val): self._set_json_field('strengths', val)

    @property
    def weaknesses_list(self): return self._get_json_field('weaknesses')
    @weaknesses_list.setter
    def weaknesses_list(self, val): self._set_json_field('weaknesses', val)

    def to_dict(self):
        """Convert object fields into dictionary for API usage."""
        return {
            'id': self.id,
            'resume_id': self.resume_id,
            'job_id': self.job_id,
            'skill_match_pct': self.skill_match_pct,
            'education_match': self.education_match,
            'experience_match': self.experience_match,
            'ats_score': self.ats_score,
            'keyword_coverage': self.keyword_coverage,
            'missing_skills': self.missing_skills_list,
            'extra_skills': self.extra_skills_list,
            'recommended_skills': self.recommended_skills_list,
            'semantic_similarity': self.semantic_similarity,
            'tfidf_similarity': self.tfidf_similarity,
            'cosine_similarity': self.cosine_similarity,
            'overall_rank': self.overall_rank,
            'prediction_label': self.prediction_label,
            'prediction_confidence': self.prediction_confidence,
            'strengths': self.strengths_list,
            'weaknesses': self.weaknesses_list,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<MatchResult Resume:{self.resume_id} Job:{self.job_id} ATS Score:{self.ats_score}>"
