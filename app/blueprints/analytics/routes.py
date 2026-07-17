"""
analytics/routes.py — Analytics & BI blueprint
Skill distribution, score trends, department breakdowns, and insights.
"""
from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app.utils.decorators import role_required
from app.extensions import db
from app.models.resume import Resume
from app.models.job_description import JobDescription
from app.models.match_result import MatchResult
from sqlalchemy import func
from collections import Counter
import json

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')


def _build_skill_frequency():
    """Count how often each skill appears across all analyzed resumes."""
    from app.models.resume import CandidateProfile
    counter = Counter()
    for profile in CandidateProfile.query.filter(CandidateProfile.skills != None).all():
        skills = profile.skills_list or []
        counter.update(skills)
    top = counter.most_common(20)
    return [s[0] for s in top], [s[1] for s in top]


def _build_score_distribution():
    """Bucket ATS overall scores into 10-point bands."""
    bands = {f'{i}-{i+9}': 0 for i in range(0, 100, 10)}
    for m in MatchResult.query.all():
        score = int(float(m.overall_score or 0))
        band_key = f'{(score // 10) * 10}-{(score // 10) * 10 + 9}'
        if band_key in bands:
            bands[band_key] += 1
    return list(bands.keys()), list(bands.values())


def _build_experience_histogram():
    """Distribution of years of experience."""
    from app.models.resume import CandidateProfile
    bins = {'0-1': 0, '2-3': 0, '4-5': 0, '6-8': 0, '9-12': 0, '13+': 0}
    for p in CandidateProfile.query.filter(CandidateProfile.total_experience_years != None).all():
        y = float(p.total_experience_years or 0)
        if y <= 1: bins['0-1'] += 1
        elif y <= 3: bins['2-3'] += 1
        elif y <= 5: bins['4-5'] += 1
        elif y <= 8: bins['6-8'] += 1
        elif y <= 12: bins['9-12'] += 1
        else: bins['13+'] += 1
    return list(bins.keys()), list(bins.values())


@analytics_bp.route('/')
@login_required
@role_required('recruiter', 'admin')
def overview():
    skill_labels, skill_counts = _build_skill_frequency()
    score_labels, score_counts = _build_score_distribution()
    exp_labels, exp_counts = _build_experience_histogram()

    total_resumes = Resume.query.count()
    total_jobs = JobDescription.query.count()
    total_matches = MatchResult.query.count()
    avg_score = db.session.query(func.avg(MatchResult.overall_score)).scalar() or 0

    from app.models.resume import CandidateProfile
    education_counts = {}
    for p in CandidateProfile.query.all():
        if p.education_list:
            edu = p.education_list[0]
            lvl = edu.get('degree', 'Unknown') if isinstance(edu, dict) else str(edu)
        else:
            lvl = 'Unknown'
        education_counts[lvl] = education_counts.get(lvl, 0) + 1

    return render_template('analytics/overview.html',
        skill_labels=json.dumps(skill_labels),
        skill_counts=json.dumps(skill_counts),
        score_labels=json.dumps(score_labels),
        score_counts=json.dumps(score_counts),
        exp_labels=json.dumps(exp_labels),
        exp_counts=json.dumps(exp_counts),
        education_labels=json.dumps(list(education_counts.keys())),
        education_counts=json.dumps(list(education_counts.values())),
        total_resumes=total_resumes,
        total_jobs=total_jobs,
        total_matches=total_matches,
        avg_score=round(float(avg_score), 1)
    )


@analytics_bp.route('/skills')
@login_required
@role_required('recruiter', 'admin')
def skills_breakdown():
    skill_labels, skill_counts = _build_skill_frequency()
    return render_template('analytics/skills.html',
        skill_labels=json.dumps(skill_labels),
        skill_counts=json.dumps(skill_counts)
    )


@analytics_bp.route('/api/stats')
@login_required
@role_required('recruiter', 'admin')
def api_stats():
    """JSON endpoint for live dashboard widget refresh."""
    skill_labels, skill_counts = _build_skill_frequency()
    score_labels, score_counts = _build_score_distribution()
    return jsonify({
        'skills': {'labels': skill_labels, 'data': skill_counts},
        'scores': {'labels': score_labels, 'data': score_counts},
        'totals': {
            'resumes': Resume.query.count(),
            'jobs': JobDescription.query.count(),
            'matches': MatchResult.query.count()
        }
    })
