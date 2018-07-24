from flask import render_template, current_app
from app.email import send_email


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[ESPCI Bar] Reset your password',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt.j2',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html.j2',
                                         user=user, token=token))
