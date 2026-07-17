import json
from datetime import datetime
from app.extensions import db

class Skill(db.Model):
    """Skill database model representing a master skills taxonomy."""
    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    category = db.Column(db.String(50))  # programming_languages, web_frameworks, databases, devops_tools, data_science, soft_skills, certifications_keywords, etc.
    aliases = db.Column(db.Text)         # JSON list of synonyms (e.g., ["JS", "ES6"] for Javascript)
    demand_score = db.Column(db.Float, default=0.0)  # relative popularity score
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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

    @property
    def aliases_list(self):
        return self._get_json_field('aliases')

    @aliases_list.setter
    def aliases_list(self, val):
        self._set_json_field('aliases', val)

    def to_dict(self):
        """Convert object fields into dictionary for API usage."""
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'aliases': self.aliases_list,
            'demand_score': self.demand_score,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<Skill {self.name} ({self.category})>"
