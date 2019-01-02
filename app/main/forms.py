# -*- coding: utf-8 -*-
"""Forms for the main blueprint."""
import safe
from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, FloatField, \
                    IntegerField, BooleanField, DateField, FieldList, \
                    SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, \
                               optional
from app.models import User, Item


class EditProfileForm(FlaskForm):
    """User profile editing form."""

    # Personal info
    first_name = StringField('First name', validators=[DataRequired()])
    last_name = StringField('Last name', validators=[DataRequired()])
    nickname = StringField('Nickname')
    birthdate = DateField(
        "Birthdate", format="%Y/%m/%d",
        validators=[DataRequired()]
        )

    # Technical info
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password')
    password2 = PasswordField('Repeat password',
                              validators=[EqualTo('password')])

    account_type = SelectField(
        'Account type',
        choices=[('observer', 'Observer'), ('customer', 'Customer'),
                 ('bartender', 'Bartender'), ('admin', 'Administrator')])

    submit = SubmitField('Submit')

    def __init__(self, original_email, *args, **kwargs):
        """Store original email to validate the new one."""
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_email = original_email

    def validate_email(self, email):
        """Validate email."""
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('Please use a different email address.')

    def validate_password(self, password):
        """Validate password."""
        if password.data != '' and repr(safe.check(password.data)) != 'strong':
            raise ValidationError("Password isn't strong enough.")


class EditItemForm(FlaskForm):
    """Item editing form."""

    name = StringField('Name', validators=[DataRequired()])
    quantity = IntegerField('Quantity (empty if not quantifiable)',
                            [optional()])
    price = FloatField('Price', validators=[DataRequired()])
    is_alcohol = BooleanField('Alcohol')
    is_quantifiable = BooleanField('Quantifiable')
    is_favorite = BooleanField('Favorite')

    submit = SubmitField('Submit')

    def __init__(self, original_name, *args, **kwargs):
        """Store original name to validate the new one."""
        super(EditItemForm, self).__init__(*args, **kwargs)
        self.original_name = original_name

    def validate_name(self, name):
        """Validate name."""
        if name.data != self.original_name:
            item = Item.query.filter_by(name=name.data).first()
            if item is not None:
                raise ValidationError('Please use a different name.')

    def validate_quantity(self, quantity):
        """Check that quantity is a strictly positive number."""
        if quantity.data is not None and quantity.data < 0:
            raise ValidationError('Please enter a positive quantity.')

    def validate_price(self, price):
        """Check that price is a strictly positive number."""
        if price.data < 0:
            raise ValidationError('Please enter a positive price.')


class AddItemForm(FlaskForm):
    """Item adding form."""

    name = StringField('Name', validators=[DataRequired()])
    quantity = IntegerField('Quantity (empty if not quantifiable)',
                            [optional()])
    price = FloatField('Price', validators=[DataRequired()])
    is_alcohol = BooleanField('Alcohol')
    is_quantifiable = BooleanField('Quantifiable')
    is_favorite = BooleanField('Favorite')

    submit = SubmitField('Submit')

    def validate_name(self, name):
        """Validate name."""
        item = Item.query.filter_by(name=name.data).first()

        if item is not None:
            raise ValidationError('Please use a different name.')

    def validate_quantity(self, quantity):
        """Check that quantity is a strictly positive number."""
        if quantity.data is not None and quantity.data < 0:
            raise ValidationError('Please enter a positive quantity.')

    def validate_price(self, price):
        """Check that price is a strictly positive number."""
        if price.data < 0:
            raise ValidationError('Please enter a positive price.')


class SearchForm(FlaskForm):
    """User search form."""

    q = StringField('Search')

    def __init__(self, *args, **kwargs):
        """Store GET arguments and CSRF status."""
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)


class GlobalSettingsForm(FlaskForm):
    """Global settings form."""

    value = FieldList(IntegerField('Key'))

    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        """Populate form with existing values."""
        super(GlobalSettingsForm, self).__init__(*args, **kwargs)
        if 'obj' in kwargs and kwargs['obj'] is not None:
            self.value.label.text = kwargs['obj'].key
