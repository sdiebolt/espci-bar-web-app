# -*- coding: utf-8 -*-
"""Main blueprint package."""
from flask import Blueprint

bp = Blueprint('main', __name__)

from app.main import routes # noqa
