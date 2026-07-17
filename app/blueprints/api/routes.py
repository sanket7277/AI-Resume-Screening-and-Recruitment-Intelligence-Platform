"""
api/routes.py — REST API blueprint (v1)
JSON endpoints for search, candidate data, and match results.
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models.resume import Resume, CandidateProfile
from app.models.job_description import JobDescription
from app.models.match_result import MatchResult

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')


def _api_error(message, code=400):
    return jsonify({'success': False, 'error': message}), code


def _api_ok(data, message='OK'):
    return jsonify({'success': True, 'message': message, 'data': data})


@api_bp.route('/search')
@login_required
def search():
    """Full-text search over candidate names and skills."""
    q = request.args.get('q', '').strip()
    limit = min(request.args.get('limit', 20, type=int), 100)

    if not q or len(q) < 2:
        return _api_error('Query must be at least 2 characters.')

    q_lower = f'%{q.lower()}%'
    results = Resume.query.join(CandidateProfile).filter(
        (CandidateProfile.name.ilike(q_lower)) |
        (CandidateProfile.email.ilike(q_lower)) |
        (Resume.raw_text.ilike(q_lower))
    ).limit(limit).all()

    data = []
    for r in results:
        # Filter skill list for query relevance
        skills = [s for s in (r.skills or []) if q.lower() in s.lower()]
        if not skills:
            skills = (r.skills or [])[:5]
        data.append({
            'id': r.id,
            'name': r.candidate_name,
            'email': r.parsed_email,
            'skills': skills,
            'experience_years': r.experience_years,
            'ats_score': None,  # Would need a specific job context
            'status': r.status
        })

    return _api_ok(data)


@api_bp.route('/resumes')
@login_required
def list_resumes():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)

    if current_user.role in ('admin', 'recruiter'):
        query = Resume.query
    else:
        query = Resume.query.filter_by(user_id=current_user.id)

    pagination = query.order_by(Resume.upload_date.desc()).paginate(page=page, per_page=per_page, error_out=False)
    data = [{
        'id': r.id,
        'candidate_name': r.candidate_name,
        'status': r.status,
        'skills': r.skills or [],
        'experience_years': r.experience_years,
        'education_level': r.education_level,
        'created_at': r.created_at.isoformat() if r.created_at else None
    } for r in pagination.items]

    return _api_ok(data)


@api_bp.route('/resumes/<int:resume_id>')
@login_required
def get_resume(resume_id):
    r = Resume.query.get_or_404(resume_id)
    if current_user.role == 'candidate' and r.user_id != current_user.id:
        return _api_error('Access denied.', 403)

    return _api_ok({
        'id': r.id,
        'candidate_name': r.candidate_name,
        'email': r.parsed_email,
        'phone': r.parsed_phone,
        'skills': r.skills or [],
        'experience_years': r.experience_years,
        'education_level': r.education_level,
        'status': r.status
    })


@api_bp.route('/jobs')
@login_required
def list_jobs():
    jobs = JobDescription.query.filter_by(is_active=True).order_by(JobDescription.created_at.desc()).limit(50).all()
    return _api_ok([{
        'id': j.id,
        'title': j.title,
        'company': j.company,
        'department': j.department,
        'location': j.location,
        'required_skills': j.required_skills or [],
        'created_at': j.created_at.isoformat() if j.created_at else None
    } for j in jobs])


@api_bp.route('/matches/<int:job_id>')
@login_required
def get_matches(job_id):
    matches = (MatchResult.query
        .filter_by(job_id=job_id)
        .order_by(MatchResult.overall_score.desc())
        .limit(50).all())

    return _api_ok([{
        'resume_id': m.resume_id,
        'overall_score': round(float(m.overall_score or 0), 2),
        'skill_match_pct': round(float(m.skill_match_pct or 0), 2),
        'semantic_similarity': round(float(m.semantic_similarity or 0), 4),
        'matched_skills': m.matched_skills or [],
        'missing_skills': m.missing_skills or [],
        'recommendation': m.recommendation or ''
    } for m in matches])


@api_bp.route('/stats/overview')
@login_required
def stats_overview():
    from app.extensions import db
    from sqlalchemy import func
    return _api_ok({
        'total_resumes': Resume.query.count(),
        'total_jobs': JobDescription.query.count(),
        'total_matches': MatchResult.query.count(),
        'avg_ats_score': round(float(
            db.session.query(func.avg(MatchResult.overall_score)).scalar() or 0
        ), 2)
    })
