"""Flask app configuration."""
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    """Flask app configuration variables."""

    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("No secret key set for Flask application")
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_TYPE = os.environ.get('SESSION_TYPE')

    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['barman@foyerespci.fr', 'samuel.diebolt@espci.psl.eu',
              'prohibition136@gmail.com']

    USERS_PER_PAGE = int(os.environ.get('USERS_PER_PAGE'))
    ITEMS_PER_PAGE = int(os.environ.get('ITEMS_PER_PAGE'))

    CURRENT_GRAD_CLASS = int(os.environ.get('CURRENT_GRAD_CLASS'))

    # Default values for global settings
    MINUTES_BEFORE_NEXT_DRINK = \
        int(os.environ.get('MINUTES_BEFORE_NEXT_DRINK'))
    MAX_ALCOHOLIC_DRINKS_PER_DAY = \
        int(os.environ.get('MAX_ALCOHOLIC_DRINKS_PER_DAY'))
    DAYS_BEFORE_INACTIVE = int(os.environ.get('DAYS_BEFORE_INACTIVE'))
    MINIMUM_LEGAL_AGE = int(os.environ.get('MINIMUM_LEGAL_AGE'))
    QUICK_ACCESS_ITEM_ID = int(os.environ.get('QUICK_ACCESS_ITEM_ID'))
