"""
admin/routes.py — Admin blueprint
User management, platform settings, and system health.
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.user import User
from app.models.resume import Resume
from app.models.job_description import JobDescription
from app.models.match_result import MatchResult
from app.utils.decorators import role_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/')
@login_required
@role_required('admin')
def index():
    return redirect(url_for('admin.users'))


@admin_bp.route('/users')
@login_required
@role_required('admin')
def users():
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('admin/users.html', users=users)


@admin_bp.route('/users/<int:user_id>/toggle-active', methods=['POST'])
@login_required
@role_required('admin')
def toggle_user_active(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot deactivate yourself.', 'warning')
    else:
        user.is_active = not user.is_active
        db.session.commit()
        state = 'activated' if user.is_active else 'deactivated'
        flash(f'User {user.username} {state}.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/change-role', methods=['POST'])
@login_required
@role_required('admin')
def change_role(user_id):
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role', 'candidate')
    if new_role not in ('candidate', 'recruiter', 'admin'):
        flash('Invalid role.', 'danger')
    else:
        user.role = new_role
        db.session.commit()
        flash(f'Role updated to {new_role}.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/settings')
@login_required
@role_required('admin')
def settings():
    from flask import current_app
    config_snapshot = {
        'UPLOAD_FOLDER': current_app.config.get('UPLOAD_FOLDER', 'N/A'),
        'MAX_CONTENT_LENGTH_MB': current_app.config.get('MAX_CONTENT_LENGTH', 0) // (1024 * 1024),
        'SQLALCHEMY_DATABASE_URI': current_app.config.get('SQLALCHEMY_DATABASE_URI', 'N/A')[:50] + '...',
        'DEBUG': current_app.config.get('DEBUG', False),
    }
    return render_template('admin/settings.html', config=config_snapshot)


@admin_bp.route('/api/health')
@login_required
@role_required('admin')
def health():
    """System health check endpoint."""
    try:
        db.session.execute(db.text('SELECT 1'))
        db_ok = True
    except Exception:
        db_ok = False

    return jsonify({
        'status': 'healthy' if db_ok else 'degraded',
        'database': 'ok' if db_ok else 'error',
        'resumes_total': Resume.query.count(),
        'users_total': User.query.count()
    })
