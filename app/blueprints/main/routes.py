"""
main/routes.py — Main / public blueprint
Landing page and about page.
"""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return render_template('index.html')


@main_bp.route('/about')
def about():
    return render_template('about.html')


@main_bp.app_errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404


@main_bp.app_errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500
