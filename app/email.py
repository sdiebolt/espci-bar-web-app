"""Main email functions."""

from threading import Thread
from flask import current_app
from flask_mail import Message
from app import mail


def send_async_email(app, msg):
    """Send async email.

    Keyword arguments:
    app -- Flask app instance
    msg -- email contents
    """
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    """Create a thread with send_async_email().

    Keyword arguments:
    subject -- email subject
    sender -- email sender
    recipients -- email recipients
    text_body -- email text_body
    html_body -- email html contents
    """
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg)).start()
