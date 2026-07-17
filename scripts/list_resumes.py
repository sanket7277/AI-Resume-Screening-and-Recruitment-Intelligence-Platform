from run import app
from app.extensions import db
from app.models.resume import Resume
from app.models.user import User

with app.app_context():
    resumes = Resume.query.all()
    for r in resumes:
        u = User.query.get(r.user_id)
        uname = u.username if u else "unknown"
        print(f"ID={r.id} | User={uname} | Name={r.parsed_name} | Email={r.parsed_email} | Status={r.status}")
