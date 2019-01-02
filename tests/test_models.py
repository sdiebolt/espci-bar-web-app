# -*- coding: utf-8 -*-
"""Test models."""
import pytest
import hashlib
from app.models import GlobalSetting, load_user


@pytest.mark.usefixtures('client', 'db', 'auth', 'item', 'all_users')
class TestUser():
    """Test User model."""

    def test_get_by_id(self, all_users):
        """Get user by ID."""
        retrieved = load_user(all_users.id)
        assert retrieved == all_users

    def test_check_password(self, all_users):
        """Check password."""
        assert all_users.check_password(all_users.username)
        assert not all_users.check_password('foobar')

    def test_qr(self, all_users):
        """Check qr."""
        # md5 encode qrcode_hash to get jpg filename
        qrcode_name = hashlib.md5()
        qrcode_name.update(all_users.qrcode_hash.encode('utf-8'))
        assert all_users.qr() == '/static/img/qr/' + qrcode_name.hexdigest() +\
            '.jpg'

        all_users.qrcode_hash = 'foobar'
        assert not all_users.qr() ==\
            '/static/img/qr/'+qrcode_name.hexdigest()+'.jpg'

    def test_can_buy(self, db, all_users, item):
        """Check user right to buy products."""
        all_users.balance = 10
        all_users.deposit = True

        minimum_legal_age = GlobalSetting.query.\
            filter_by(key='MINIMUM_LEGAL_AGE').first().value
        max_daily_alcoholic_drinks_per_user = GlobalSetting.query.\
            filter_by(key='MAX_DAILY_ALCOHOLIC_DRINKS_PER_USER').first().value

        non_alcohol = item(name='non_alcohol', is_alcohol=False, quantity=1)
        alcohol = item(name='alcohol', is_alcohol=True,
                       quantity=max_daily_alcoholic_drinks_per_user+1)
        db.session.add(non_alcohol)
        db.session.add(alcohol)

        db.session.commit()

        assert all_users.can_buy(None) == 'No item selected.'

        assert all_users.can_buy(non_alcohol) is True
        assert all_users.can_buy(alcohol) ==\
            "{} {} isn't old enough, the minimum legal age being {}.".\
            format(all_users.first_name, all_users.last_name,
                   minimum_legal_age)
