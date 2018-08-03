import os.path
from datetime import datetime, timedelta
from time import time
from flask import current_app, url_for, flash
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import db, login
from app.search import add_to_index, remove_from_index, query_index

class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)

db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)

class User(SearchableMixin, UserMixin, db.Model):
    __searchable__ = ['username', 'email', 'first_name', 'last_name',
                        'nickname', 'grad_class']

    id = db.Column(db.Integer, primary_key=True)

    # Login info
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    # Personal info
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    nickname = db.Column(db.String(64), index=True)
    is_barman = db.Column(db.Boolean, default=False)
    grad_class = db.Column(db.Integer, index=True, default=0)

    # Technical info
    balance = db.Column(db.Float, default=0.0)
    last_drink = db.Column(db.DateTime, default=datetime.utcnow)
    transactions = db.relationship('Transaction', backref='client',
                                    lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self):
        avatar_path = 'img/avatar/'+str(self.grad_class)+'/'+self.username
        if os.path.isfile(os.path.join('app', 'static', avatar_path+'.jpg')):
            avatar_filename = url_for('static', filename=avatar_path+'.jpg')
            return avatar_filename
        elif os.path.isfile(os.path.join('app', 'static', avatar_path+'.png')):
            avatar_filename = url_for('static', filename=avatar_path+'.png')
            return avatar_filename
        else:
            return url_for('static', filename='img/avatar_placeholder.png')

    def qr(self):
        qr_path = 'img/qr/'+self.username+'_qr'
        if os.path.isfile(os.path.join('app', 'static', qr_path+'.jpg')):
            qr_filename = url_for('static', filename=qr_path+'.jpg')
            return qr_filename
        elif os.path.isfile(os.path.join('app', 'static', qr_path+'.png')):
            qr_filename = url_for('static', filename=qr_path+'.png')
            return qr_filename

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    def can_buy(self, item):
        """ Return the user's right to buy the item depending on his balance
            and the time since his last drink if the item is alcohol. """
        if item.is_alcohol and self.last_drink > (datetime.utcnow() - timedelta(minutes=30)):
            return False
        elif self.balance < item.price:
            return False
        else:
            return True

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithm=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(64), index=True, unique=True)
    is_alcohol = db.Column(db.Boolean)
    price = db.Column(db.Float)
    is_quantifiable = db.Column(db.Boolean)
    quantity = db.Column(db.Integer, default=0)

    def __repr__(self):
        return '<Item {}>'.format(self.name)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # type can be 'Top up', 'Pay <Item>' or 'Edit balance'
    type = db.Column(db.String(64), index=True)
    balance_change = db.Column(db.Float)

    def __repr__(self):
        return '<Transaction {}>'.format(self.date)
