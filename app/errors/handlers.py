# -*- coding: utf-8 -*-
"""View functions for the error routes."""
from flask import render_template
from app import db
from app.errors import bp


@bp.app_errorhandler(404)
def not_found_error(error):
    """Render error 404 page."""
    return render_template('errors/404.html.j2'), 404


@bp.app_errorhandler(500)
def internal_error(error):
    """Render error 500 page."""
    db.session.rollback()
    return render_template('errors/500.html.j2'), 500
