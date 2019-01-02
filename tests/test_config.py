# -*- coding: utf-8 -*-
"""Test configs."""
from app import create_app
from config import DevelopmentConfig, ProductionConfig


def test_production_config():
    """Production config."""
    app = create_app(ProductionConfig)
    assert app.config['ENV'] == 'production'
    assert not app.config['DEBUG']


def test_dev_config():
    """Development config."""
    app = create_app(DevelopmentConfig)
    assert app.config['ENV'] == 'development'
    assert app.config['DEBUG']
