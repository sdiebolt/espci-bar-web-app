import os
from flask import url_for
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Login info
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    # Personal info
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    is_barman = db.Column(db.Boolean, default=False)
    grad_class = db.Column(db.Integer, index=True, default=0)

    # Technical info
    balance = db.Column(db.Float, default=0.0)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self):
        avatar_filename = url_for('static', filename='img/'+self.username+'.jpg')
        return avatar_filename

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
