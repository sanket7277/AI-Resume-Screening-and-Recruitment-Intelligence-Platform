import json
from datetime import datetime, date
from app.extensions import db

class AnalyticsSnapshot(db.Model):
    """AnalyticsSnapshot database model representing cached HR dashboard snapshot metrics."""
    __tablename__ = 'analytics_snapshots'

    id = db.Column(db.Integer, primary_key=True)
    snapshot_date = db.Column(db.Date, default=date.today, unique=True, index=True)
    
    total_resumes = db.Column(db.Integer, default=0)
    total_jobs = db.Column(db.Integer, default=0)
    total_matches = db.Column(db.Integer, default=0)
    avg_ats_score = db.Column(db.Float, default=0.0)
    
    # Complex charts data stored as JSON strings
    top_skills = db.Column(db.Text)          # JSON list of dicts: [{"skill": "Python", "count": 25}, ...]
    metrics = db.Column(db.Text)             # JSON dictionary for other aggregate variables
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def _get_json_field(self, field_name):
        val = getattr(self, field_name)
        if val:
            try:
                return json.loads(val)
            except json.JSONDecodeError:
                return {}
        return {}

    def _set_json_field(self, field_name, value):
        setattr(self, field_name, json.dumps(value))

    @property
    def top_skills_list(self): return self._get_json_field('top_skills')
    @top_skills_list.setter
    def top_skills_list(self, val): self._set_json_field('top_skills', val)

    @property
    def metrics_dict(self): return self._get_json_field('metrics')
    @metrics_dict.setter
    def metrics_dict(self, val): self._set_json_field('metrics', val)

    def to_dict(self):
        """Convert object fields into dictionary for API usage."""
        return {
            'id': self.id,
            'snapshot_date': self.snapshot_date.isoformat() if self.snapshot_date else None,
            'total_resumes': self.total_resumes,
            'total_jobs': self.total_jobs,
            'total_matches': self.total_matches,
            'avg_ats_score': self.avg_ats_score,
            'top_skills': self.top_skills_list,
            'metrics': self.metrics_dict,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<AnalyticsSnapshot {self.snapshot_date}>"
