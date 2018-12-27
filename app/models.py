"""Flask app models."""

import os.path
from datetime import date, datetime, timedelta
from time import time
from flask import current_app, url_for
from flask_login import UserMixin
from sqlalchemy.sql.expression import and_
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib
import jwt
import qrcode
from app import db, login, whooshee


@whooshee.register_model('username', 'first_name', 'last_name', 'nickname')
class User(UserMixin, db.Model):
    """User model."""

    id = db.Column(db.Integer, primary_key=True)

    # Login info
    username = db.Column(db.String(64), index=True, unique=True,
                         nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    qrcode_hash = db.Column(db.String(128), nullable=False)

    # Personal info
    first_name = db.Column(db.String(64), index=True, nullable=False)
    last_name = db.Column(db.String(64), index=True, nullable=False)
    nickname = db.Column(db.String(64), index=True)
    birthdate = db.Column(db.Date, nullable=False)
    is_bartender = db.Column(db.Boolean, default=False, nullable=False)
    grad_class = db.Column(db.Integer, index=True, default=0, nullable=False)

    # Technical info
    balance = db.Column(db.Float, default=0.0, nullable=False)
    last_drink = db.Column(db.DateTime, default=None, nullable=True)
    transactions = db.relationship('Transaction', backref='client',
                                   lazy='dynamic')
    deposit = db.Column(db.Boolean, default=False)

    def __repr__(self):
        """Print user's username when printing an user object."""
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        """Set user password hash."""
        self.password_hash = generate_password_hash(password)

    def set_qrcode(self):
        """Set user QR code hash."""
        self.qrcode_hash = generate_password_hash(str(datetime.utcnow()))

        # Create QR code object
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=0,
        )
        qr.add_data(self.qrcode_hash)
        qr.make(fit=True)

        # md5 encode qrcode_hash to get jpg filename
        qrcode_name = hashlib.md5()
        qrcode_name.update(self.qrcode_hash.encode('utf-8'))

        # Create QR code image and save it to static folder
        img = qr.make_image()
        img = img.resize((160, 160))
        img.save('app/static/img/qr/'+qrcode_name.hexdigest()+'.jpg')

    def check_password(self, password):
        """Check password against stored hash."""
        return check_password_hash(self.password_hash, password)

    def avatar(self):
        """Return url for avatar file."""
        avatar_path = 'img/avatar/'+str(self.grad_class)+'/'+self.username
        if os.path.isfile(os.path.join('app', 'static', avatar_path+'.jpg')):
            avatar_filename = url_for('static', filename=avatar_path+'.jpg')
            return avatar_filename
        elif os.path.isfile(os.path.join('app', 'static', avatar_path+'.png')):
            avatar_filename = url_for('static', filename=avatar_path+'.png')
            return avatar_filename
        else:
            return url_for('static',
                           filename='img/avatar/avatar_placeholder.png')

    def qr(self):
        """Return url for qr code file."""
        # md5 encode qrcode_hash to get jpg filename
        qrcode_name = hashlib.md5()
        qrcode_name.update(self.qrcode_hash.encode('utf-8'))
        qr_path = os.path.join('img', 'qr',
                               qrcode_name.hexdigest()+'.jpg')
        if os.path.isfile(os.path.join('app', 'static', qr_path)):
            qr_filename = url_for('static', filename=qr_path)
            return qr_filename
        return None

    def get_reset_password_token(self, expires_in=600):
        """Return the reset password token."""
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').\
            decode('utf-8')

    def can_buy(self, item):
        """Return the user's right to buy the item."""
        if not item:
            return False
        today = date.today()
        age = today.year - self.birthdate.year - \
            ((today.month, today.day) <
                (self.birthdate.month, self.birthdate.day))
        nb_alcoholic_drinks = self.transactions.\
            filter_by(is_reverted=False).\
            filter(and_(Transaction.item.has(is_alcohol=True),
                        Transaction.date >
                        datetime.utcnow() - timedelta(hours=12))).count()
        if self.last_drink:
            time_to_wait = current_app.config['MINUTES_BEFORE_NEXT_DRINK'] - \
                (datetime.utcnow() - self.last_drink).seconds//60
        else:
            time_to_wait = 0
        if item.is_alcohol and age < current_app.config['MINIMUM_LEGAL_AGE']:
            return "{} {} isn't old enough, the minimum legal age being {}.".\
                format(self.first_name, self.last_name,
                       current_app.config['MINIMUM_LEGAL_AGE'])
        elif item.is_alcohol and time_to_wait > 0:
            return '{} {} must wait {} minutes to buy alcohol.'.\
                format(self.first_name, self.last_name, time_to_wait)
        elif item.is_alcohol and nb_alcoholic_drinks >= \
                current_app.config['MAX_ALCOHOLIC_DRINKS_PER_DAY']:
            return '{} {} has reached the limit of {} drinks per night.'.\
                format(self.first_name, self.last_name,
                       current_app.config['MAX_ALCOHOLIC_DRINKS_PER_DAY'])
        elif self.balance < item.price:
            return "{} {} doesn't have enough funds to buy {}.".\
                format(self.first_name, self.last_name, item.name)
        else:
            return True

    @staticmethod
    def verify_reset_password_token(token):
        """Verify reset password token validity."""
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithm=['HS256'])['reset_password']
        except Exception:
            return
        return User.query.get(id)


@login.user_loader
def load_user(id):
    """Return user from id."""
    return User.query.get(int(id))


class Item(db.Model):
    """Item model."""

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(64), index=True, unique=True, nullable=False)

    is_alcohol = db.Column(db.Boolean)

    price = db.Column(db.Float, nullable=False)

    is_quantifiable = db.Column(db.Boolean)
    quantity = db.Column(db.Integer, default=0)

    is_favorite = db.Column(db.Boolean, default=False)

    transactions = db.relationship('Transaction', backref='item',
                                   lazy='dynamic')

    def __repr__(self):
        """Print item's name when printing an item object."""
        return '<Item {}>'.format(self.name)


class Transaction(db.Model):
    """Transaction model."""

    id = db.Column(db.Integer, primary_key=True)

    # True if the transaction has been reverted. In this case, won't ever go
    # back to False
    is_reverted = db.Column(db.Boolean, default=False)

    date = db.Column(db.DateTime, index=True, default=datetime.utcnow,
                     nullable=False)

    # The barman who made the transaction
    barman = db.Column(db.String(64), index=True, nullable=False)

    # Not NULL if type is 'Pay <Item>' or 'Top up'
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Not NULL if type is 'Pay <Item>'
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))

    # type can be 'Top up', 'Pay <Item>' or 'Revert #<id>'
    type = db.Column(db.String(64), index=True, nullable=False)
    balance_change = db.Column(db.Float)

    def __repr__(self):
        """Print transaction's date when printing a transaction object."""
        return '<Transaction {}>'.format(self.date)


class GlobalSetting(db.Model):
    """App global settings model."""

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(128), nullable=False)
    key = db.Column(db.String(64), nullable=False)
    value = db.Column(db.Integer, default=0)

    def __repr__(self):
        """Print setting's key when printing a global setting object."""
        return '<Setting {}>'.format(self.key)
