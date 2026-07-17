"""
auth/routes.py — Authentication blueprint
Handles login, registration, logout, profile, and password reset.
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app.extensions import db
from app.models.user import User
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        if not email or not password:
            flash('Please enter both email and password.', 'warning')
            return render_template('auth/login.html')

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash('Invalid email or password.', 'danger')
            return render_template('auth/login.html')

        if not user.is_active:
            flash('Your account has been deactivated. Please contact support.', 'danger')
            return render_template('auth/login.html')

        login_user(user, remember=remember)
        user.last_login = datetime.utcnow()
        db.session.commit()

        next_page = request.args.get('next')
        flash(f'Welcome back, {user.username}!', 'success')
        return redirect(next_page or url_for('dashboard.index'))

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        role = request.form.get('role', 'candidate')

        # Basic validation
        errors = []
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters.')
        if not email or '@' not in email:
            errors.append('A valid email is required.')
        if len(password) < 8:
            errors.append('Password must be at least 8 characters.')
        if password != password_confirm:
            errors.append('Passwords do not match.')
        if role not in ('candidate', 'recruiter'):
            role = 'candidate'

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('An account with that email already exists.', 'danger')
            return render_template('auth/register.html')

        if User.query.filter_by(username=username).first():
            flash('That username is already taken.', 'danger')
            return render_template('auth/register.html')

        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role,
            is_active=True
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash(f'Account created! Welcome to RecruitIQ, {user.username}.', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been signed out.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.first_name = request.form.get('first_name', current_user.first_name).strip()
        current_user.last_name = request.form.get('last_name', current_user.last_name).strip()
        current_user.bio = request.form.get('bio', '').strip()
        current_user.department = request.form.get('department', '').strip()

        new_pw = request.form.get('new_password', '')
        if new_pw:
            current_pw = request.form.get('current_password', '')
            if not current_user.check_password(current_pw):
                flash('Current password is incorrect.', 'danger')
                return render_template('auth/profile.html')
            if len(new_pw) < 8:
                flash('New password must be at least 8 characters.', 'danger')
                return render_template('auth/profile.html')
            current_user.set_password(new_pw)

        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html')


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        # Stub — in production this would send a reset email
        flash('If that email exists, you will receive a reset link shortly.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/forgot_password.html')
