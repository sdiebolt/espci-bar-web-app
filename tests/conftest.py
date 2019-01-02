# -*- coding: utf-8 -*-
"""Defines fixtures available to all tests."""

import pytest
from app import create_app
from app import db as _db
from config import TestingConfig


@pytest.fixture(scope='module')
def app():
    """Yield an application for the tests."""
    _app = create_app(TestingConfig)

    with _app.app_context():
        _db.create_all()

    client = app.test_client()

    # Establish an application context before running the tests
    ctx = app.app_context()
    ctx.push()

    yield client

    ctx.pop()


@pytest.yield_fixture(scope='function')
def db(app):
    """Yield a database for the tests."""
    _db.app = app
    with app.app_context():
        _db.create_all()

    yield _db

    # Explicitly close DB connection
    _db.session.close()
    _db.drop_all()
