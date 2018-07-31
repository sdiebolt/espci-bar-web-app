import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['samuel.diebolt@espci.fr']

    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')
    NO_SEARCH_SSL = os.environ.get('NO_SEARCH_SSL')

    USERS_PER_PAGE = int(os.environ.get('USERS_PER_PAGE') or 12)
    ITEMS_PER_PAGE = int(os.environ.get('ITEMS_PER_PAGE') or 10)

    CURRENT_GRAD_CLASS = int(os.environ.get('CURRENT_GRAD_CLASS') or 136)

    MINUTES_BEFORE_NEXT_DRINK = int(os.environ.get('MINUTES_BEFORE_NEXT_DRINK') or 30)
    DAYS_BEFORE_INACTIVE = int(os.environ.get('DAYS_BEFORE_INACTIVE') or 30)
