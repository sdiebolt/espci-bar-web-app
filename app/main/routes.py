# -*- coding: utf-8 -*-
"""View functions for the main routes."""

import datetime
from calendar import monthrange
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required, fresh_login_required
from sqlalchemy import extract
from sqlalchemy.sql.expression import and_
from app import db
from app.main.forms import EditProfileForm, EditItemForm, AddItemForm, \
    SearchForm, GlobalSettingsForm
from app.models import User, Item, Transaction, GlobalSetting
from app.main import bp


@bp.before_app_request
def before_request():
    """Create the search form before each request."""
    if not current_user.is_anonymous:
        if current_user.is_bartender:
            g.search_form = SearchForm()


def month_year_iter(start_month, start_year, end_month, end_year):
    """Return month iterator."""
    ym_start = 12*start_year + start_month - 1
    ym_end = 12*end_year + end_month - 1
    for ym in range(ym_start, ym_end):
        y, m = divmod(ym, 12)
        yield y, m+1


@bp.route('/get_yearly_transactions', methods=['GET'])
@login_required
def get_yearly_transactions():
    """Return transaction from last 12 months."""
    if not (current_user.is_bartender or current_user.is_observer):
        return redirect(url_for('main.user', username=current_user.username))

    # Get current day, month, year
    today = datetime.datetime.today()
    current_year = today.year
    current_month = today.month

    # Get last 12 months range
    if current_month == 12:
        previous_year = current_year
    else:
        previous_year = current_year - 1
    previous_month = (current_month-12) % 12

    # Get money spent and topped up last 12 months
    paid_per_month = []
    topped_per_month = []
    for (y, m) in month_year_iter(previous_month+1, previous_year,
                                  current_month+1, current_year):
        transactions_paid_y = Transaction.query.\
            filter(
                and_(extract('month', Transaction.date) == m,
                     extract('year', Transaction.date) == y)).\
            filter(Transaction.type.like('Pay%')).\
            filter_by(is_reverted=False).all()
        transactions_topped_y = Transaction.query.\
            filter(
                and_(extract('month', Transaction.date) == m,
                     extract('year', Transaction.date) == y)).\
            filter(Transaction.type.like('Top up')).\
            filter_by(is_reverted=False).all()
        paid_per_month.append(0)
        for t in transactions_paid_y:
            paid_per_month[-1] -= t.balance_change
        topped_per_month.append(0)
        for t in transactions_topped_y:
            topped_per_month[-1] += t.balance_change

    # Generate months labels
    months_labels = ['%.2d' % m[1] + '/'+str(m[0]) for m in
                     list(month_year_iter(previous_month+1, previous_year,
                                          current_month+1, current_year))]

    return jsonify({'paid_per_month': paid_per_month,
                    'topped_per_month': topped_per_month,
                    'months_labels': months_labels})


@bp.route('/get_daily_statistics', methods=['GET'])
@login_required
def get_daily_statistics():
    """Return daily statistics."""
    # Get current day start
    today = datetime.datetime.today()
    yesterday = today - datetime.timedelta(days=1)
    if today.hour < 6:
        current_day_start = datetime.\
            datetime(year=yesterday.year, month=yesterday.month,
                     day=yesterday.day, hour=6)
    else:
        current_day_start = datetime.\
            datetime(year=today.year, month=today.month,
                     day=today.day, hour=6)

    # Daily clients
    nb_daily_clients = User.query.\
        filter(User.transactions.any(Transaction.date > current_day_start)).\
        count()

    # Daily alcohol consumption
    alcohol_qty = Transaction.query.\
        filter(Transaction.date > current_day_start).\
        filter(Transaction.type.like('Pay%')).\
        filter(Transaction.item.has(is_alcohol=True)).\
        filter_by(is_reverted=False).count() * 0.25

    # Daily revenue
    daily_transactions = Transaction.query.\
        filter(Transaction.date > current_day_start).\
        filter(Transaction.type.like('Pay%')).\
        filter_by(is_reverted=False).all()
    daily_revenue = sum([abs(t.balance_change) for t in daily_transactions])

    return jsonify({'nb_daily_clients': nb_daily_clients,
                    'alcohol_qty': alcohol_qty,
                    'daily_revenue': daily_revenue})


@bp.route('/', methods=['GET'])
@bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """Render the index page.

    - For admins, bartenders and observers, it renders the dashboard.
    - For customers, it redirects to the user profile.
    - For anonymous users, it redirects to the login page.
    """
    if not (current_user.is_bartender or current_user.is_observer):
        return redirect(url_for('main.user', username=current_user.username))

    # Get current day start
    today = datetime.datetime.today()
    yesterday = today - datetime.timedelta(days=1)
    current_year = today.year
    current_month = today.month
    if today.hour < 6:
        current_day_start = datetime.\
            datetime(year=yesterday.year, month=yesterday.month,
                     day=yesterday.day, hour=6)
    else:
        current_day_start = datetime.\
            datetime(year=today.year, month=today.month,
                     day=today.day, hour=6)

    # Daily clients
    nb_daily_clients = User.query.\
        filter(User.transactions.any(Transaction.date > current_day_start)).\
        count()

    # Daily alcohol consumption
    alcohol_qty = Transaction.query.\
        filter(Transaction.date > current_day_start).\
        filter(Transaction.type.like('Pay%')).\
        filter(Transaction.item.has(is_alcohol=True)).\
        filter_by(is_reverted=False).count() * 0.25

    # Daily revenue
    daily_transactions = Transaction.query.\
        filter(Transaction.date > current_day_start).\
        filter(Transaction.type.like('Pay%')).\
        filter_by(is_reverted=False).all()
    daily_revenue = sum([abs(t.balance_change) for t in daily_transactions])

    # Get money spent and topped up this month
    paid_this_month = []
    topped_this_month = []
    for day in range(1, monthrange(current_year, current_month)[1] + 1):
        transactions_paid_m = Transaction.query.\
            filter(
                and_(extract('day', Transaction.date) == day,
                     and_(extract('month', Transaction.date) == current_month,
                          extract('year', Transaction.date) == current_year))
                  ).filter(Transaction.type.like('Pay%')).\
            filter_by(is_reverted=False).all()
        transactions_topped_m = Transaction.query.\
            filter(
                and_(extract('day', Transaction.date) == day,
                     and_(extract('month', Transaction.date) == current_month,
                          extract('year', Transaction.date) == current_year))
                  ).filter(Transaction.type.like('Top up')).\
            filter_by(is_reverted=False).all()
        paid_this_month.append(0)
        for t in transactions_paid_m:
            paid_this_month[-1] -= t.balance_change
        topped_this_month.append(0)
        for t in transactions_topped_m:
            topped_this_month[-1] += t.balance_change

    # Generate days labels
    days_labels = ['%.2d' % current_month + '/' + '%.2d' % day for day in
                   range(1, monthrange(current_year, current_month)[1] + 1)]

    return render_template('dashboard.html.j2',
                           title='Dashboard',
                           paid_this_month=paid_this_month,
                           topped_this_month=topped_this_month,
                           days_labels=days_labels,
                           nb_daily_clients=nb_daily_clients,
                           alcohol_qty=alcohol_qty,
                           daily_revenue=daily_revenue)


@bp.route('/search', methods=['GET'])
@login_required
def search():
    """Render search page."""
    if not current_user.is_bartender:
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.dashboard'))
    if not g.search_form.validate():
        return redirect(url_for('main.dashboard'))

    # Get arguments
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'asc', type=str)
    query = request.args.get('q', '', type=str)

    # If the query is empty, redirect to the index page
    if query == '':
        return redirect(url_for('main.dashboard'))

    # Get inventory
    inventory = Item.query.order_by(Item.name.asc()).all()

    # Get favorite items
    favorite_inventory = Item.query.filter_by(is_favorite=True).\
        order_by(Item.name.asc()).all()

    # Get quick access item
    quick_access_item_id = GlobalSetting.query.\
        filter_by(key='QUICK_ACCESS_ITEM_ID').first()
    quick_access_item = Item.query.\
        filter_by(id=quick_access_item_id.value).first()

    # Get users corresponding to the query
    query_text = g.search_form.q.data
    final_query = User.query.whooshee_search(query_text)
    total = final_query.count()

    # Sort users alphabetically
    if sort == 'asc':
        users = final_query.\
            order_by(User.last_name.asc()).\
            paginate(page, current_app.config['USERS_PER_PAGE'], True)
    else:
        users = final_query.\
            order_by(User.last_name.desc()).\
            paginate(page, current_app.config['USERS_PER_PAGE'], True)

    # If only one user, redirect to his profile
    if total == 1:
        return redirect(url_for('main.user', username=users.items[0].username))

    return render_template('search.html.j2', title='Search', users=users,
                           sort=sort, inventory=inventory, total=total,
                           favorite_inventory=favorite_inventory,
                           quick_access_item=quick_access_item)


@bp.route('/get_user_products', methods=['GET'])
@login_required
def get_user_products():
    """Return the list of products that a user can buy."""
    if not current_user.is_bartender:
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.dashboard'))

    # Get user
    user = User.query.filter_by(username=request.args['username']).\
        first_or_404()

    # Get inventory
    inventory = Item.query.order_by(Item.name.asc()).all()

    # Get favorite items
    favorite_inventory = Item.query.filter_by(is_favorite=True).\
        order_by(Item.name.asc()).all()

    pay_template = render_template('_user_products.html.j2', user=user,
                                   inventory=inventory,
                                   favorite_inventory=favorite_inventory)

    return jsonify({'html': pay_template})


@bp.route('/user/<username>', methods=['GET'])
@login_required
def user(username):
    """Render the user profile page.

    Keyword arguments:
    username -- the user's username
    """
    if current_user.username != username and (not current_user.is_bartender):
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.dashboard'))

    # Get transactions page
    page = request.args.get('page', 1, type=int)

    # Get user
    user = User.query.filter_by(username=username).first_or_404()

    today = datetime.date.today()
    age = today.year - user.birthdate.year - \
        ((today.month, today.day) < (user.birthdate.month, user.birthdate.day))

    # Get user transactions
    transactions = user.transactions.order_by(Transaction.id.desc()).\
        paginate(page, 5, True)

    # Get inventory
    inventory = Item.query.order_by(Item.name.asc()).all()

    # Get favorite items
    favorite_inventory = Item.query.filter_by(is_favorite=True).\
        order_by(Item.name.asc()).all()

    # Get quick access item
    quick_access_item_id = GlobalSetting.query.\
        filter_by(key='QUICK_ACCESS_ITEM_ID').first()
    quick_access_item = Item.query.\
        filter_by(id=quick_access_item_id.value).first()

    return render_template('user.html.j2', title=username + ' profile',
                           age=age, user=user,
                           inventory=inventory,
                           favorite_inventory=favorite_inventory,
                           quick_access_item=quick_access_item,
                           transactions=transactions)


@bp.route('/edit_profile/<username>', methods=['GET', 'POST'])
@fresh_login_required
def edit_profile(username):
    """Render the user editing page.

    Keyword arguments:
    username -- the user's username
    """
    if not current_user.is_admin:
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.dashboard'))

    user = User.query.filter_by(username=username).first_or_404()
    form = EditProfileForm(user.email)
    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.birthdate = form.birthdate.data
        user.nickname = form.nickname.data
        user.email = form.email.data

        # Set account type
        user.is_customer = form.account_type.data == 'customer' or \
            form.account_type.data == 'observer' or \
            form.account_type.data == 'bartender' or \
            form.account_type.data == 'admin'
        user.is_observer = form.account_type.data == 'observer' or \
            form.account_type.data == 'bartender' or \
            form.account_type.data == 'admin'
        user.is_bartender = form.account_type.data == 'bartender' or \
            form.account_type.data == 'admin'
        user.is_admin = form.account_type.data == 'admin'

        if (form.password.data != ''):
            user.set_password(form.password.data)
        db.session.commit()
        flash('Your changes have been saved.', 'primary')
        return redirect(url_for('main.user', username=user.username))
    elif request.method == 'GET':
        form.first_name.data = user.first_name
        form.last_name.data = user.last_name
        form.birthdate.data = user.birthdate
        form.nickname.data = user.nickname
        form.email.data = user.email
        if user.is_observer:
            form.account_type.data = 'observer'
        if user.is_customer:
            form.account_type.data = 'customer'
        if user.is_bartender:
            form.account_type.data = 'bartender'
        if user.is_admin:
            form.account_type.data = 'admin'
    return render_template('edit_profile.html.j2', title='Edit profile',
                           form=form)


@bp.route('/deposit', methods=['GET'])
@login_required
def deposit():
    """Set a user deposit state."""
    if not current_user.is_bartender:
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.dashboard'))

    username = request.args.get('username', None, type=str)
    user = User.query.filter_by(username=username).first_or_404()

    if user.deposit is True:
        flash('User already gave a deposit.', 'warning')
        return redirect(request.referrer)

    user.deposit = True
    db.session.commit()

    return redirect(request.referrer)


@bp.route('/delete_user', methods=['GET'])
@fresh_login_required
def delete_user():
    """Delete a user."""
    if not current_user.is_admin:
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.dashboard'))

    username = request.args.get('username', None, type=str)

    user = User.query.filter_by(username=username).first_or_404()
    db.session.delete(user)
    db.session.commit()
    flash('The user ' + username + ' has been deleted.', 'primary')
    return redirect(url_for('main.dashboard'))


@bp.route('/transactions')
@login_required
def transactions():
    """Render the transactions page."""
    if not current_user.is_bartender:
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.dashboard'))

    # Get arguments
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'desc', type=str)

    # Sort transactions alphabetically
    if sort == 'asc':
        transactions = Transaction.query.order_by(Transaction.id.asc()).\
            paginate(page, current_app.config['ITEMS_PER_PAGE'], True)
    else:
        transactions = Transaction.query.order_by(Transaction.id.desc()).\
            paginate(page, current_app.config['ITEMS_PER_PAGE'], True)

    return render_template('transactions.html.j2', title='Transactions',
                           transactions=transactions, sort=sort)


@bp.route('/revert_transaction')
@login_required
def revert_transaction():
    """Revert a transaction."""
    if not current_user.is_bartender:
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.dashboard'))

    transaction_id = request.args.get('transaction_id', -1, type=int)

    # Transactions that are already reverted can't be reverted again
    transaction = Transaction.query.filter_by(id=transaction_id).first_or_404()
    if transaction.is_reverted or 'Revert' in transaction.type:
        flash("You can't revert this transaction.", 'warning')
        return redirect(request.referrer)

    # Revert client balance
    if transaction.client:
        # Check if user balance stays positive before reverting
        if transaction.client.balance - transaction.balance_change < 0:
            flash(transaction.client.first_name + ' ' +
                  transaction.client.last_name + '\'s balance would be ' +
                  'negative if this transaction were reverted.', 'warning')
            return redirect(request.referrer)
        transaction.client.balance -= transaction.balance_change
        if transaction.item and transaction.item.is_alcohol:
            transaction.client.last_drink = None

    # Revert item quantity
    if transaction.item and transaction.item.is_quantifiable:
        transaction.item.quantity += 1

    # Transaction is now reverted: it won't ever be 'unreverted'
    transaction.is_reverted = True

    transaction = Transaction(client_id=None,
                              barman=current_user.username,
                              date=datetime.datetime.utcnow(),
                              type='Revert #'+str(transaction_id),
                              balance_change=None)

    db.session.add(transaction)
    db.session.commit()

    flash('The transaction #'+str(transaction_id)+' has been reverted.',
          'primary')
    return redirect(request.referrer)


@bp.route('/inventory')
@login_required
def inventory():
    """Render the inventory page."""
    if not current_user.is_bartender:
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.dashboard'))

    # Get arguments
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'asc', type=str)

    # Get quick access item
    quick_access_item_id = GlobalSetting.query.\
        filter_by(key='QUICK_ACCESS_ITEM_ID').first()
    quick_access_item = Item.query.\
        filter_by(id=quick_access_item_id.value).first()

    # Sort items alphabetically
    if sort == 'asc':
        inventory = Item.query.order_by(Item.name.asc()).\
            paginate(page, current_app.config['ITEMS_PER_PAGE'], True)
    else:
        inventory = Item.query.order_by(Item.name.desc()).\
            paginate(page, current_app.config['ITEMS_PER_PAGE'], True)

    return render_template('inventory.html.j2', title='Inventory',
                           inventory=inventory, sort=sort,
                           quick_access_item=quick_access_item)


@bp.route('/set_quick_access_item')
@login_required
def set_quick_access_item():
    """Set the quick access item."""
    if not current_user.is_bartender:
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.dashboard'))

    # Get arguments
    item_name = request.args.get('item_name', None, type=str)

    # Get item
    item = Item.query.filter_by(name=item_name).first_or_404()

    # Get quick access item id
    quick_access_item_id = GlobalSetting.query.\
        filter_by(key='QUICK_ACCESS_ITEM_ID').first()

    # Update the quick access item id
    quick_access_item_id.value = item.id
    db.session.commit()

    return redirect(request.referrer)


@bp.route('/add_item', methods=['GET', 'POST'])
@login_required
def add_item():
    """Add an item to the inventory."""
    if not current_user.is_bartender:
        flash("You don't have the rights to acces this page.", 'danger')
        return redirect(url_for('main.dashboard'))

    form = AddItemForm()
    if form.validate_on_submit():
        quantity = form.quantity.data
        if quantity is None:
            quantity = 0
        item = Item(name=form.name.data, quantity=quantity,
                    price=form.price.data, is_alcohol=form.is_alcohol.data,
                    is_quantifiable=form.is_quantifiable.data,
                    is_favorite=form.is_favorite.data)
        db.session.add(item)
        db.session.commit()
        flash('The item '+item.name+' was successfully added.', 'primary')
        return redirect(url_for('main.inventory'))
    return render_template('add_item.html.j2', title='Add item', form=form)


@bp.route('/edit_item/<item_name>', methods=['GET', 'POST'])
@fresh_login_required
def edit_item(item_name):
    """Render the item editing page.

    Keyword arguments:
    item_name -- the item's name
    """
    if not current_user.is_bartender:
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.dashboard'))

    item = Item.query.filter_by(name=item_name).first_or_404()
    form = EditItemForm(item.name)
    if form.validate_on_submit():
        quantity = form.quantity.data
        if quantity is None:
            quantity = 0
        item.name = form.name.data
        if item.is_quantifiable:
            item.quantity = quantity
        item.price = form.price.data
        item.is_alcohol = form.is_alcohol.data
        item.is_quantifiable = form.is_quantifiable.data
        item.is_favorite = form.is_favorite.data
        db.session.commit()
        flash('Your changes have been saved.', 'primary')
        return redirect(url_for('main.inventory'))
    elif request.method == 'GET':
        form.name.data = item.name
        if item.is_quantifiable:
            form.quantity.data = item.quantity
        form.price.data = item.price
        form.is_alcohol.data = item.is_alcohol
        form.is_quantifiable.data = item.is_quantifiable
        form.is_favorite.data = item.is_favorite
    return render_template('edit_item.html.j2', title='Edit item',
                           form=form)


@bp.route('/delete_item')
@login_required
def delete_item():
    """Delete an item from the inventory."""
    if not current_user.is_bartender:
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.dashboard'))

    item_name = request.args.get('item_name', None, type=str)

    item = Item.query.filter_by(name=item_name).first_or_404()
    db.session.delete(item)
    db.session.commit()
    flash('The item ' + item_name + ' has been deleted.', 'primary')
    return redirect(request.referrer)


@bp.route('/top_up', methods=['GET', 'POST'])
@login_required
def top_up():
    """Top up the user's balance and redirect to the last page."""
    if not current_user.is_bartender:
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.dashboard'))

    username = request.args.get('username', 'none', type=str)
    user = User.query.filter_by(username=username).first_or_404()

    amount = request.form.get('amount', 0, type=float)

    if amount <= 0:
        flash('Please enter a strictly positive value.', 'warning')
        return redirect(request.referrer)

    user = User.query.filter_by(username=username).first_or_404()
    user.balance += amount

    transaction = Transaction(client_id=user.id, barman=current_user.username,
                              date=datetime.datetime.utcnow(), type='Top up',
                              balance_change=amount)
    db.session.add(transaction)
    db.session.commit()

    flash('You added ' + str(amount) + '€ to ' + user.first_name + ' ' +
          user.last_name + "'s account. " +
          render_template('_revert_button.html.j2', transaction=transaction),
          'primary')
    return redirect(request.referrer)


@bp.route('/pay', methods=['GET'])
@login_required
def pay():
    """Substract the item price to the user's balance."""
    if not current_user.is_bartender:
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.dashboard'))

    username = request.args.get('username', 'none', type=str)
    item_name = request.args.get('item_name', 'none', type=str)

    user = User.query.filter_by(username=username).first_or_404()
    item = Item.query.filter_by(name=item_name).first_or_404()

    if not user.deposit:
        flash(user.username+" hasn't given a deposit.", 'warning')
        return redirect(request.referrer)

    user_can_buy = user.can_buy(item)
    if user_can_buy is not True:
        flash(user_can_buy, 'warning')
        return redirect(request.referrer)

    if item.is_quantifiable and item.quantity <= 0:
        flash('No '+item.name+' left.', 'warning')
        return redirect(request.referrer)

    user.balance -= item.price
    if item.is_quantifiable:
        item.quantity -= 1
    if item.is_alcohol:
        user.last_drink = datetime.datetime.utcnow()

    transaction = Transaction(client_id=user.id, item_id=item.id,
                              barman=current_user.username,
                              date=datetime.datetime.utcnow(),
                              type='Pay ' + item.name,
                              balance_change=-item.price)
    db.session.add(transaction)
    db.session.commit()

    flash(user.first_name + ' ' + user.last_name + ' successfully bought ' +
          item.name +
          ' (Balance: {:.2f}'.format(user.balance)+'€). ' +
          render_template('_revert_button.html.j2', transaction=transaction),
          'primary')
    return redirect(request.referrer)


@bp.route('/scanqrcode')
@login_required
def scanqrcode():
    """Render the QR code scanner page."""
    if not current_user.is_bartender:
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.dashboard'))

    return render_template('scanqrcode.html.j2', title='Scan QR code')


@bp.route('/get_user_from_qr')
@login_required
def get_user_from_qr():
    """Redirect to the user profile corresponding to the QR code."""
    if not current_user.is_bartender:
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.dashboard'))

    # Get arguments
    qrcode_hash = request.args.get('qrcode_hash', 'None', type=str)

    # Retrieve corresponding user
    user = User.query.filter_by(qrcode_hash=qrcode_hash).first_or_404()

    return redirect(url_for('main.user', username=user.username))


@bp.route('/qrcode/<username>')
@login_required
def qrcode(username):
    """Render the user QR code page.

    Keyword arguments:
    username -- the user's username
    """
    if current_user.username != username and (not current_user.is_bartender):
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.dashboard'))

    user = User.query.filter_by(username=username).first_or_404()

    return render_template('qrcode.html.j2', title='QR code', user=user)


@bp.route('/global_settings', methods=['GET', 'POST'])
@login_required
def global_settings():
    """Render the global settings page."""
    if not current_user.is_admin:
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.dashboard'))

    form = GlobalSettingsForm()
    if form.validate_on_submit():
        settings = GlobalSetting.query.all()
        for index, s in enumerate(settings):
            s.value = form.value.data[index]
        db.session.commit()
        flash('Global settings successfully updated.', 'primary')
        return redirect(url_for('main.global_settings'))
    else:
        settings = GlobalSetting.query.all()
        for index, s in enumerate(settings):
            form.value.append_entry(s.value)
            form.value.entries[index].label.text = s.name
    return render_template('global_settings.html.j2', title='Global settings',
                           form=form)
