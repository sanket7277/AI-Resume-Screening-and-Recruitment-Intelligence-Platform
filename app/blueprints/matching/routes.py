"""
matching/routes.py — ATS Matching & Ranking blueprint
Run matching engine, view score breakdowns, compare candidates, and export rankings.
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, make_response, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.models.resume import Resume
from app.models.job_description import JobDescription
from app.models.match_result import MatchResult
from app.utils.decorators import role_required
import csv
import io

matching_bp = Blueprint('matching', __name__, url_prefix='/matching')


@matching_bp.route('/')
@login_required
@role_required('recruiter', 'admin')
def index():
    """Matching hub — shows recent match runs."""
    jobs = JobDescription.query.filter_by(is_active=True).order_by(JobDescription.created_at.desc()).limit(20).all()
    recent_matches = MatchResult.query.order_by(MatchResult.created_at.desc()).limit(10).all()
    return render_template('matching/index.html', jobs=jobs, recent_matches=recent_matches)


@matching_bp.route('/run', methods=['POST'])
@login_required
@role_required('recruiter', 'admin')
def run_match():
    """Run the matching engine for a specific job against all (or selected) resumes."""
    job_id = request.form.get('job_id', type=int)
    resume_ids_raw = request.form.getlist('resume_ids')

    if not job_id:
        flash('Please select a job to match against.', 'warning')
        return redirect(url_for('matching.index'))

    job = JobDescription.query.get_or_404(job_id)

    if resume_ids_raw:
        resumes = Resume.query.filter(Resume.id.in_([int(x) for x in resume_ids_raw if x.isdigit()])).all()
    else:
        resumes = Resume.query.filter_by(status='analyzed').all()

    if not resumes:
        flash('No analyzed resumes available to match.', 'warning')
        return redirect(url_for('matching.index'))

    from app.services.matching_engine import MatchingEngine
    engine = MatchingEngine()

    matched_count = 0
    for resume in resumes:
        try:
            scores = engine.compute_match(resume, job)
            # Upsert match result
            existing = MatchResult.query.filter_by(resume_id=resume.id, job_id=job.id).first()
            if existing:
                mr = existing
            else:
                mr = MatchResult(resume_id=resume.id, job_id=job.id)
                db.session.add(mr)

            mr.overall_score = scores['overall_score']
            mr.skill_match_pct = scores.get('skill_match_pct', 0)
            mr.semantic_similarity = scores.get('semantic_similarity', 0)
            mr.keyword_coverage = scores.get('keyword_coverage', 0)
            mr.experience_match = scores.get('experience_match', 0)
            mr.education_match = scores.get('education_match', 0)
            mr.matched_skills_list = scores.get('matched_skills', [])
            mr.missing_skills_list = scores.get('missing_skills', [])
            mr.extra_skills_list = scores.get('extra_skills', [])
            mr.recommendation = scores.get('recommendation', '')
            matched_count += 1
        except Exception as ex:
            current_app.logger.warning(f'Match failed for resume {resume.id}: {ex}')

    db.session.commit()
    flash(f'Matched {matched_count} resume(s) against "{job.title}".', 'success')
    return redirect(url_for('matching.results', job_id=job_id))


@matching_bp.route('/results/<int:job_id>')
@login_required
@role_required('recruiter', 'admin')
def results(job_id):
    """Ranked candidate list for a job."""
    job = JobDescription.query.get_or_404(job_id)
    matches = (MatchResult.query
        .filter_by(job_id=job_id)
        .order_by(MatchResult.overall_score.desc())
        .all())
    return render_template('matching/results.html', job=job, matches=matches)


@matching_bp.route('/detail/<int:match_id>')
@login_required
def detail(match_id):
    """Full breakdown for a single candidate–job match."""
    match = MatchResult.query.get_or_404(match_id)
    resume = Resume.query.get_or_404(match.resume_id)
    if current_user.role == 'candidate' and resume.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard.index'))
    job = JobDescription.query.get_or_404(match.job_id)
    return render_template('matching/detail.html', match=match, resume=resume, job=job)


@matching_bp.route('/compare/<int:job_id>')
@login_required
@role_required('recruiter', 'admin')
def compare(job_id):
    """Side-by-side comparison of top candidates."""
    job = JobDescription.query.get_or_404(job_id)
    top = (MatchResult.query
        .filter_by(job_id=job_id)
        .order_by(MatchResult.overall_score.desc())
        .limit(3).all())
    resumes = [Resume.query.get(m.resume_id) for m in top]
    return render_template('matching/compare.html', job=job, matches=top, resumes=resumes)


@matching_bp.route('/export/<int:job_id>')
@login_required
@role_required('recruiter', 'admin')
def export_csv(job_id):
    """Download ranked candidates as CSV."""
    job = JobDescription.query.get_or_404(job_id)
    matches = MatchResult.query.filter_by(job_id=job_id).order_by(MatchResult.overall_score.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Rank', 'Candidate', 'Email', 'ATS Score', 'Skill Match%', 'Semantic Sim.', 'Missing Skills', 'Recommendation'])

    for i, m in enumerate(matches, 1):
        resume = Resume.query.get(m.resume_id)
        writer.writerow([
            i,
            resume.candidate_name if resume else 'Unknown',
            resume.parsed_email if resume else '',
            round(float(m.overall_score or 0), 1),
            round(float(m.skill_match_pct or 0), 1),
            round(float(m.semantic_similarity or 0), 3),
            ', '.join(m.missing_skills or []),
            m.recommendation or ''
        ])

    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=rankings_{job.title.replace(" ","_")}.csv'
    return response
