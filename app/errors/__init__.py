# -*- coding: utf-8 -*-
"""Errors blueprint package."""
from flask import Blueprint

bp = Blueprint('errors', __name__)

from app.errors import handlers # noqa
