# -*- coding: utf-8 -*-
"""Test models."""
import pytest
import hashlib
import datetime
from app.models import GlobalSetting, load_user


@pytest.mark.usefixtures('client', 'db', 'auth', 'all_users',
                         'non_alcohol_item', 'alcohol_item')
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

    def test_can_buy_deposit(self, db, all_users, non_alcohol_item):
        """Test can_buy() with and whithout deposit."""
        assert all_users.can_buy(non_alcohol_item) ==\
            "{} {} hasn't given a deposit.".\
            format(all_users.first_name, all_users.last_name)

    def test_can_buy_none(self, db, all_users):
        """Test can_buy() without item."""
        all_users.deposit = True
        db.session.commit()
        assert all_users.can_buy(None) == 'No item selected.'

    def test_can_buy_no_item_left(self, db, all_users, non_alcohol_item):
        """Test can_buy() with zero item quantity."""
        all_users.deposit = True
        db.session.commit()
        assert all_users.can_buy(non_alcohol_item) ==\
            'No {} left.'.format(non_alcohol_item.name)

    def test_can_buy_alcohol_underage(self, db, all_users, alcohol_item):
        """Test can_buy() with underage user and alcohol item."""
        all_users.deposit = True
        alcohol_item.quantity = 1
        db.session.commit()

        minimum_legal_age = GlobalSetting.query.\
            filter_by(key='MINIMUM_LEGAL_AGE').first().value

        assert all_users.can_buy(alcohol_item) ==\
            "{} {} isn't old enough, the minimum legal age being {}.".\
            format(all_users.first_name, all_users.last_name,
                   minimum_legal_age)

    def test_can_buy_drink_limit(self, db, all_users, alcohol_item):
        """Test can_buy() with drink limit reached."""
        all_users.deposit = True
        alcohol_item.quantity = 1

        minimum_legal_age = GlobalSetting.query.\
            filter_by(key='MINIMUM_LEGAL_AGE').first().value
        today = datetime.datetime.today()
        all_users.birthdate = datetime.datetime(
            year=today.year-minimum_legal_age-1,
            month=1,
            day=1)

        max_daily_alcoholic_drinks_per_user = GlobalSetting.query.\
            filter_by(key='MAX_DAILY_ALCOHOLIC_DRINKS_PER_USER').first()
        max_daily_alcoholic_drinks_per_user.value = 0

        db.session.commit()

        assert all_users.can_buy(alcohol_item) ==\
            '{} {} has reached the limit of {} drinks per night.'.\
            format(all_users.first_name, all_users.last_name,
                   max_daily_alcoholic_drinks_per_user.value)

    def test_can_buy_no_balance(self, db, all_users, non_alcohol_item):
        """Test can_buy() without balance."""
        all_users.deposit = True
        non_alcohol_item.quantity = 1
        db.session.commit()

        assert all_users.can_buy(non_alcohol_item) ==\
            "{} {} doesn't have enough funds to buy {}.".\
            format(all_users.first_name, all_users.last_name,
                   non_alcohol_item.name)

    def test_can_buy_alcohol_success(self, db, all_users, alcohol_item):
        """Test can_buy() success with alcohol item."""
        all_users.deposit = True
        all_users.balance = 1
        alcohol_item.quantity = 1

        minimum_legal_age = GlobalSetting.query.\
            filter_by(key='MINIMUM_LEGAL_AGE').first().value
        today = datetime.datetime.today()
        all_users.birthdate = datetime.datetime(
            year=today.year-minimum_legal_age-1,
            month=1,
            day=1)

        db.session.commit()

        assert all_users.can_buy(alcohol_item) is True
