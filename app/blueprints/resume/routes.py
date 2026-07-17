"""
resume/routes.py — Resume management blueprint
Upload, view, list, delete, and trigger NLP analysis.
"""
import os
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models.resume import Resume
from app.utils.file_handler import save_uploaded_file, delete_resume_file
from app.utils.decorators import role_required

resume_bp = Blueprint('resume', __name__, url_prefix='/resume')

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}


def _allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@resume_bp.route('/')
@login_required
def list_resumes():
    page = request.args.get('page', 1, type=int)
    per_page = 12

    if current_user.role in ('admin', 'recruiter'):
        query = Resume.query.order_by(Resume.upload_date.desc())
    else:
        query = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.upload_date.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('resume/list.html', resumes=pagination.items, pagination=pagination)


@resume_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'resume_file' not in request.files:
            flash('No file selected.', 'warning')
            return redirect(request.url)

        file = request.files['resume_file']
        if file.filename == '':
            flash('No file selected.', 'warning')
            return redirect(request.url)

        if not _allowed_file(file.filename):
            flash('Invalid file type. Upload PDF, DOCX, or TXT only.', 'danger')
            return redirect(request.url)

        # Persist file
        try:
            file_path, file_size = save_uploaded_file(file, current_app.config['UPLOAD_FOLDER'])
        except Exception as ex:
            current_app.logger.error(f'File upload failed: {ex}')
            flash('File upload failed. Please try again.', 'danger')
            return redirect(request.url)

        filename = os.path.basename(file_path)
        resume = Resume(
            user_id=current_user.id,
            filename=filename,
            original_filename=secure_filename(file.filename),
            file_size=file_size,
            file_type=file.filename.rsplit('.', 1)[1].lower(),
            status='pending'
        )
        db.session.add(resume)
        db.session.flush()

        # Create candidate profile stub immediately
        candidate_name = request.form.get('candidate_name', '').strip() or file.filename.rsplit('.', 1)[0]
        from app.models.resume import CandidateProfile
        profile = CandidateProfile(
            resume_id=resume.id,
            name=candidate_name
        )
        db.session.add(profile)
        db.session.commit()

        # Kick off NLP parsing in a background-friendly way
        try:
            _run_nlp_analysis(resume)
        except Exception as ex:
            current_app.logger.warning(f'NLP parsing deferred (resume {resume.id}): {ex}')

        flash('Resume uploaded and queued for analysis.', 'success')
        return redirect(url_for('resume.view', resume_id=resume.id))

    return render_template('resume/upload.html')


def _run_nlp_analysis(resume: Resume):
    """Parse the resume file and populate structured fields."""
    from app.services.resume_parser import ResumeParser
    from app.services.nlp_pipeline import NLPPipeline
    from app.models.resume import CandidateProfile

    parser = ResumeParser()
    pipeline = NLPPipeline()

    try:
        parsed_data = parser.parse(resume.file_path)
        raw_text = parsed_data.get('raw_text', '')
    except Exception as e:
        current_app.logger.error(f"Parser error: {e}")
        raw_text = ""
        
    if not raw_text:
        resume.status = 'failed'
        db.session.commit()
        return

    result = pipeline.process_resume(raw_text)
    resume.raw_text = raw_text

    profile = resume.candidate_profile
    if not profile:
        profile = CandidateProfile(resume_id=resume.id)
        db.session.add(profile)

    profile.name = result.get('name', '') or profile.name
    profile.email = result.get('email', '')
    profile.phone = result.get('phone', '')
    profile.location = result.get('location', '')
    profile.summary = result.get('summary', '')
    profile.skills_list = result.get('skills', [])
    profile.experience_list = result.get('experience', [])
    profile.education_list = result.get('education', [])
    profile.total_experience_years = float(result.get('total_experience_years', 0))

    resume.status = 'analyzed'
    db.session.commit()


@resume_bp.route('/view/<int:resume_id>')
@login_required
def view(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    # Candidates can only view their own resumes
    if current_user.role == 'candidate' and resume.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('resume.list_resumes'))

    from app.models.match_result import MatchResult
    matches = MatchResult.query.filter_by(resume_id=resume_id).order_by(MatchResult.overall_score.desc()).limit(5).all()
    return render_template('resume/view.html', resume=resume, matches=matches)


@resume_bp.route('/delete/<int:resume_id>', methods=['POST'])
@login_required
def delete(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    if current_user.role == 'candidate' and resume.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('resume.list_resumes'))

    try:
        delete_resume_file(resume.file_path)
    except Exception:
        pass  # File may already be missing

    db.session.delete(resume)
    db.session.commit()
    flash('Resume deleted.', 'info')
    return redirect(url_for('resume.list_resumes'))


@resume_bp.route('/analyze/<int:resume_id>', methods=['POST'])
@login_required
def re_analyze(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    if current_user.role == 'candidate' and resume.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('resume.list_resumes'))
    try:
        _run_nlp_analysis(resume)
        flash('Resume re-analyzed successfully.', 'success')
    except Exception as ex:
        flash(f'Analysis failed: {str(ex)[:120]}', 'danger')
    return redirect(url_for('resume.view', resume_id=resume_id))
