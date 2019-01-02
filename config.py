# -*- coding: utf-8 -*-
"""Application configuration."""
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    """Base configuration."""

    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("No secret key set for Flask application")

    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')

    USERS_PER_PAGE = int(os.environ.get('USERS_PER_PAGE'))
    ITEMS_PER_PAGE = int(os.environ.get('ITEMS_PER_PAGE'))

    CURRENT_GRAD_CLASS = int(os.environ.get('CURRENT_GRAD_CLASS'))

    # Default values for global settings
    MAX_DAILY_ALCOHOLIC_DRINKS_PER_USER = \
        int(os.environ.get('MAX_DAILY_ALCOHOLIC_DRINKS_PER_USER'))
    MINIMUM_LEGAL_AGE = int(os.environ.get('MINIMUM_LEGAL_AGE'))
    QUICK_ACCESS_ITEM_ID = int(os.environ.get('QUICK_ACCESS_ITEM_ID'))


class ProductionConfig(Config):
    """Production configuration."""

    ENV = 'production'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


class DevelopmentConfig(Config):
    """Development configuration."""

    ENV = 'development'
    DEBUG = True
    DB_NAME = 'dev.db'
    DB_PATH = os.path.join(Config.PROJECT_ROOT, DB_NAME)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{0}'.format(DB_PATH)


class TestingConfig(Config):
    """Test configuration."""

    TESTING = True
    DEBUG = True
    DB_NAME = 'testing.db'
    DB_PATH = os.path.join(Config.PROJECT_ROOT, DB_NAME)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{0}'.format(DB_PATH)
