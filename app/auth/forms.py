# -*- coding: utf-8 -*-
"""Forms for the authentication blueprint."""
from flask_wtf import FlaskForm
import datetime
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    IntegerField, DateField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, optional
from app.models import User


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign in')


class RegistrationForm(FlaskForm):
    """Registration form."""

    # Personal info
    first_name = StringField('First name', validators=[DataRequired()])
    last_name = StringField('Last name', validators=[DataRequired()])
    birthdate = DateField(
        "Birthdate", format="%Y/%m/%d",
        default=datetime.datetime.today,
        validators=[DataRequired()]
        )
    email = StringField('Email', validators=[DataRequired(), Email()])
    grad_class = IntegerField('Graduating class (empty if non student)',
                              [optional()])

    account_type = SelectField(
        'Account type',
        choices=[('observer', 'Observer'), ('customer', 'Customer'),
                 ('bartender', 'Bartender'), ('admin', 'Administrator')])

    submit = SubmitField('Register')

    def validate_email(self, email):
        """Validate email."""
        user = User.query.filter_by(email=email.data).first()

        if user is not None:
            raise ValidationError('Please use a different email address.')

    def validate_grad_class(self, grad_class):
        """Validate grad_class."""
        if grad_class.data is not None and grad_class.data < 0:
            raise ValidationError('Please enter a valid graduating class or '
                                  'nothing if non student.')
