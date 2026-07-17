"""
dashboard/routes.py — Dashboard blueprint
Serves role-specific dashboard views: admin overview, recruiter pipeline, candidate status.
"""
from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.user import User
from app.models.resume import Resume
from app.models.job_description import JobDescription
from app.models.match_result import MatchResult
from sqlalchemy import func
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


def _get_common_stats():
    """Build shared KPI numbers used across all dashboard roles."""
    total_resumes = Resume.query.count()
    total_jobs = JobDescription.query.count()
    total_matches = MatchResult.query.count()
    avg_score = db.session.query(func.avg(MatchResult.overall_score)).scalar() or 0
    return {
        'total_resumes': total_resumes,
        'total_jobs': total_jobs,
        'total_matches': total_matches,
        'avg_score': round(float(avg_score), 1)
    }


@dashboard_bp.route('/')
@dashboard_bp.route('')
@login_required
def index():
    role = current_user.role

    if role == 'admin':
        return _admin_dashboard()
    elif role == 'recruiter':
        return _recruiter_dashboard()
    else:
        return _candidate_dashboard()


def _admin_dashboard():
    stats = _get_common_stats()
    stats['total_users'] = User.query.count()
    stats['active_users'] = User.query.filter_by(is_active=True).count()

    # Score distribution for chart
    score_bins = {'0-25': 0, '26-50': 0, '51-75': 0, '76-100': 0}
    for r in MatchResult.query.all():
        s = float(r.overall_score or 0)
        if s <= 25: score_bins['0-25'] += 1
        elif s <= 50: score_bins['26-50'] += 1
        elif s <= 75: score_bins['51-75'] += 1
        else: score_bins['76-100'] += 1

    # Recent activity
    recent_resumes = Resume.query.order_by(Resume.upload_date.desc()).limit(5).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()

    return render_template('dashboard/admin.html',
        stats=stats,
        score_bins=score_bins,
        recent_resumes=recent_resumes,
        recent_users=recent_users
    )


def _recruiter_dashboard():
    # Only resumes matched against jobs this recruiter posted
    my_jobs = JobDescription.query.filter_by(created_by=current_user.id).all()
    job_ids = [j.id for j in my_jobs]

    top_matches = (MatchResult.query
        .filter(MatchResult.job_id.in_(job_ids))
        .order_by(MatchResult.overall_score.desc())
        .limit(10).all()) if job_ids else []

    stats = {
        'my_jobs': len(my_jobs),
        'total_candidates': Resume.query.count(),
        'matches_run': MatchResult.query.filter(MatchResult.job_id.in_(job_ids)).count() if job_ids else 0,
        'avg_score': 0
    }
    if top_matches:
        stats['avg_score'] = round(sum(float(m.overall_score or 0) for m in top_matches) / len(top_matches), 1)

    return render_template('dashboard/recruiter.html',
        stats=stats,
        my_jobs=my_jobs,
        top_matches=top_matches
    )


def _candidate_dashboard():
    my_resumes = Resume.query.filter_by(user_id=current_user.id).all()
    resume_ids = [r.id for r in my_resumes]

    my_matches = (MatchResult.query
        .filter(MatchResult.resume_id.in_(resume_ids))
        .order_by(MatchResult.overall_score.desc())
        .limit(5).all()) if resume_ids else []

    best_score = max((float(m.overall_score or 0) for m in my_matches), default=0)

    return render_template('dashboard/candidate.html',
        my_resumes=my_resumes,
        my_matches=my_matches,
        best_score=round(best_score, 1),
        resume_count=len(my_resumes)
    )
