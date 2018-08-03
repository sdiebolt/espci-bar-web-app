from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, FloatField, IntegerField, BooleanField
from wtforms.validators import ValidationError, DataRequired, Length, Email, EqualTo, NumberRange, optional
from app.models import User, Item


class EditProfileForm(FlaskForm):
    # Personal info
    first_name = StringField('First name', validators=[DataRequired()])
    last_name = StringField('Last name', validators=[DataRequired()])

    # Technical info
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password')
    password2 = PasswordField('Repeat password',
                                validators=[EqualTo('password')])

    is_barman = BooleanField('Barman')

    submit = SubmitField('Submit')

    def __init__(self, original_email, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_email = original_email

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('Please use a different email address.')

class EditItemForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    quantity = IntegerField('Quantity (empty if not quantifiable)', [optional()])
    price = FloatField('Price', validators=[DataRequired()])
    is_alcohol = BooleanField('Alcohol')
    is_quantifiable = BooleanField('Quantifiable')

    submit = SubmitField('Submit')

    def __init__(self, original_name, *args, **kwargs):
        super(EditItemForm, self).__init__(*args, **kwargs)
        self.original_name = original_name

    def validate_name(self, name):
        if name.data != self.original_name:
            item = Item.query.filter_by(name=name.data).first()
            if item is not None:
                raise ValidationError('Please use a different name.')

    def validate_quantity(self, quantity):
        if quantity.data is not None and quantity.data < 0:
            raise ValidationError('Please enter a positive quantity.')

    def validate_price(self, price):
        if price.data < 0:
            raise ValidationError('Please enter a positive price.')

class AddItemForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    quantity = IntegerField('Quantity (empty if not quantifiable)', [optional()])
    price = FloatField('Price', validators=[DataRequired()])
    is_alcohol = BooleanField('Alcohol')
    is_quantifiable = BooleanField('Quantifiable')

    submit = SubmitField('Submit')

    def validate_name(self, name):
        item = Item.query.filter_by(name=name.data).first()

        if item is not None:
            raise ValidationError('Please use a different name.')

    def validate_quantity(self, quantity):
        if quantity.data is not None and quantity.data < 0:
            raise ValidationError('Please enter a positive quantity.')

    def validate_price(self, price):
        if price.data < 0:
            raise ValidationError('Please enter a positive price.')

class SearchForm(FlaskForm):
    q = StringField('Search', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)
