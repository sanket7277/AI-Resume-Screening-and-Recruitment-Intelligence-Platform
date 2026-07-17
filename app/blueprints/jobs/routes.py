"""
jobs/routes.py — Job Description blueprint
Create, view, list, edit, and delete job postings.
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.job_description import JobDescription
from app.utils.decorators import role_required

jobs_bp = Blueprint('jobs', __name__, url_prefix='/jobs')


@jobs_bp.route('/')
@login_required
def list_jobs():
    page = request.args.get('page', 1, type=int)
    if current_user.role == 'admin':
        jobs = JobDescription.query.order_by(JobDescription.created_at.desc()).paginate(page=page, per_page=10)
    elif current_user.role == 'recruiter':
        jobs = JobDescription.query.filter_by(created_by=current_user.id).order_by(JobDescription.created_at.desc()).paginate(page=page, per_page=10)
    else:
        # Candidates see all active job listings
        jobs = JobDescription.query.filter_by(is_active=True).order_by(JobDescription.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('jobs/list.html', jobs=jobs)


@jobs_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required('recruiter', 'admin')
def create():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        company = request.form.get('company', '').strip()
        department = request.form.get('department', '').strip()
        location = request.form.get('location', '').strip()
        employment_type = request.form.get('employment_type', 'Full-time')
        description = request.form.get('description', '').strip()
        requirements = request.form.get('requirements', '').strip()
        min_experience = request.form.get('min_experience', 0, type=int)
        education_required = request.form.get('education_required', '').strip()
        salary_min = request.form.get('salary_min', None, type=int)
        salary_max = request.form.get('salary_max', None, type=int)

        if not title or not description:
            flash('Job title and description are required.', 'danger')
            return render_template('jobs/create.html')

        # Extract required skills from requirements text
        required_skills = []
        if requirements:
            from app.nlp.keyword_extractor import KeywordExtractor
            try:
                extractor = KeywordExtractor()
                required_skills = extractor.extract_skills_from_text(requirements)
            except Exception:
                pass

        job = JobDescription(
            title=title,
            company=company,
            department=department,
            location=location,
            employment_type=employment_type,
            description=description,
            requirements=requirements,
            min_experience=min_experience,
            education_required=education_required,
            salary_min=salary_min,
            salary_max=salary_max,
            required_skills=required_skills,
            created_by=current_user.id,
            is_active=True
        )
        db.session.add(job)
        db.session.commit()
        flash(f'Job "{title}" created successfully.', 'success')
        return redirect(url_for('jobs.detail', job_id=job.id))

    return render_template('jobs/create.html')


@jobs_bp.route('/<int:job_id>')
@login_required
def detail(job_id):
    job = JobDescription.query.get_or_404(job_id)
    from app.models.match_result import MatchResult
    matches = MatchResult.query.filter_by(job_id=job_id).order_by(MatchResult.overall_score.desc()).limit(10).all()
    return render_template('jobs/detail.html', job=job, matches=matches)


@jobs_bp.route('/<int:job_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('recruiter', 'admin')
def edit(job_id):
    job = JobDescription.query.get_or_404(job_id)
    if current_user.role == 'recruiter' and job.created_by != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('jobs.list_jobs'))

    if request.method == 'POST':
        job.title = request.form.get('title', job.title).strip()
        job.company = request.form.get('company', job.company).strip()
        job.department = request.form.get('department', '').strip()
        job.location = request.form.get('location', '').strip()
        job.description = request.form.get('description', job.description).strip()
        job.requirements = request.form.get('requirements', '').strip()
        job.is_active = bool(request.form.get('is_active'))
        db.session.commit()
        flash('Job updated.', 'success')
        return redirect(url_for('jobs.detail', job_id=job_id))

    return render_template('jobs/edit.html', job=job)


@jobs_bp.route('/<int:job_id>/delete', methods=['POST'])
@login_required
@role_required('recruiter', 'admin')
def delete(job_id):
    job = JobDescription.query.get_or_404(job_id)
    if current_user.role == 'recruiter' and job.created_by != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('jobs.list_jobs'))
    db.session.delete(job)
    db.session.commit()
    flash('Job deleted.', 'info')
    return redirect(url_for('jobs.list_jobs'))
