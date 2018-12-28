"""Flask application init file.

Creates the app instance to eliminate the need of a global app variable.
"""

import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_whooshee import Whooshee
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Please log in to access this page.'
login.login_message_category = 'warning'
mail = Mail()
moment = Moment()
whooshee = Whooshee()


def create_app(config_class=Config):
    """Create a Flask application instance."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    whooshee.init_app(app)

    # Initialize global settings from database
    from app.models import GlobalSetting
    with app.app_context():
        # Create database entries if they don't exist yet
        global_settings = {
            'MAX_DAILY_ALCOHOLIC_DRINKS_PER_USER':
                'Maximum daily number of alcoholic drinks per user '
                '(0 for infinite)',
            'MINIMUM_LEGAL_AGE':
                'Minimum legal age',
            'QUICK_ACCESS_ITEM_ID':
                'Quick access item'
            }
        for key, name in global_settings.items():
            if GlobalSetting.query.filter_by(key=key).first() is None:
                gs = GlobalSetting(key=key, value=app.config[key], name=name)
                db.session.add(gs)
            db.session.commit()

    # Register error, auth and main blueprints
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    # Flask logs
    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'],
                        app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='noreply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='ESPCI Bar Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)
        if app.config['LOG_TO_STDOUT']:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
        else:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/espcibar.log',
                                               maxBytes=10240, backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s '
                '[in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('ESPCI Bar startup')

    return app

from app import models
