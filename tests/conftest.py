# -*- coding: utf-8 -*-
"""Defines fixtures available to all tests."""
import pytest
import re
from flask import url_for
from app import create_app
from app import db as _db
from app.models import User, Item, GlobalSetting
from config import TestingConfig


@pytest.fixture
def app():
    """Yield an application for the tests."""
    _app = create_app(TestingConfig)

    with _app.app_context():
        _db.create_all()

        minimum_legal_age = GlobalSetting(
            name='Minimum legal age',
            key='MINIMUM_LEGAL_AGE',
            value=18
        )
        max_daily_alcoholic_drinks_per_user = GlobalSetting(
            name='Maximum daily number of alcoholic drinks per user '
                 '(0 for infinite)',
            key='MAX_DAILY_ALCOHOLIC_DRINKS_PER_USER',
            value=4
        )
        quick_access_item_id = GlobalSetting(
            name='Quick access item id',
            key='QUICK_ACCESS_ITEM_ID',
            value=1
        )
        _db.session.add(minimum_legal_age)
        _db.session.add(max_daily_alcoholic_drinks_per_user)
        _db.session.add(quick_access_item_id)
        _db.session.commit()

    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture
def client(app):
    """Return client for the tests."""
    return app.test_client()


@pytest.fixture
def db(app):
    """Yield a database for the tests."""
    _db.app = app
    with app.app_context():
        _db.create_all()

    yield _db

    # Explicitly close DB connection
    _db.session.close()
    _db.drop_all()


@pytest.fixture
def user(db):
    """Return a user creation function for the tests."""
    def make_user(username, account_type='customer'):
        # Create user
        user = User(
            username=username,
            email=username+'@localhost',
            first_name=username,
            last_name=username,
            nickname=username,
        )

        # Set account type
        user.is_customer = account_type == 'customer' or \
            account_type == 'observer' or \
            account_type == 'bartender' or \
            account_type == 'admin'
        user.is_observer = account_type == 'observer' or \
            account_type == 'bartender' or \
            account_type == 'admin'
        user.is_bartender = account_type == 'bartender' or \
            account_type == 'admin'
        user.is_admin = account_type == 'admin'

        # Set password and qrcode hashes
        user.set_password(username)
        user.set_qrcode()

        return user

    return make_user


@pytest.fixture(params=['customer', 'observer', 'bartender', 'admin'])
def all_users(request, db, user):
    """Yield all user types for the tests."""
    u = user(username=request.param, account_type=request.param)

    db.session.add(u)
    db.session.commit()

    yield u

    db.session.delete(u)
    db.session.commit()


@pytest.fixture
def auth(client):
    """Return a user authentication function for the tests."""
    def auth_user(username, password):
        rv = client.get(url_for('auth.login'))
        m = re.search(b'(<input id="csrf_token" name="csrf_token" '
                      b'type="hidden" value=")([-A-Za-z.0-9]+)', rv.data)

        return client.post(url_for('auth.login'), data=dict(
            username=username,
            password=password,
            csrf_token=m.group(2).decode("utf-8")
        ), follow_redirects=True)

    return auth_user


@pytest.fixture
def item(app):
    """Return an item creation function for the tests."""
    def make_item(name='test', is_alcohol=False, quantity=0):
        # Create item
        item = Item(
            name=name,
            is_alcohol=is_alcohol,
            price=1,
            is_quantifiable=True,
            quantity=quantity
        )

        return item

    return make_item


@pytest.fixture
def non_alcohol_item(db, item):
    """Yield a non alcohol item for the tests."""
    i = item(name='non_alcohol')

    db.session.add(i)
    db.session.commit()

    yield i

    db.session.delete(i)
    db.session.commit()


@pytest.fixture
def alcohol_item(db, item):
    """Yield an alcohol item for the tests."""
    i = item(name='alcohol', is_alcohol=True)

    db.session.add(i)
    db.session.commit()

    yield i

    db.session.delete(i)
    db.session.commit()
