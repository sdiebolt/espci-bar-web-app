import datetime
from calendar import monthrange
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required, fresh_login_required
from sqlalchemy.sql.expression import and_
from sqlalchemy import extract
from app import db
from app.main.forms import EditProfileForm, EditItemForm, AddItemForm, \
    SearchForm, GlobalSettingsForm
from app.models import User, Item, Transaction, GlobalSetting
from app.main import bp


@bp.before_app_request
def before_request():
    if not current_user.is_anonymous:
        if current_user.is_bartender:
            g.search_form = SearchForm()

@bp.route('/', methods=['GET'])
@bp.route('/index', methods=['GET'])
@login_required
def index():
    """ View index page. For barmen, it's the customers page and for clients,
        it redirects to the profile. """
    if not current_user.is_bartender:
        return redirect(url_for('main.user', username=current_user.username))

    # Get arguments
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'asc', type=str)
    grad_class = request.args.get('grad_class', str(current_app.config['CURRENT_GRAD_CLASS']), type=int)

    # Get graduating classes
    grad_classes_query = db.session.query(User.grad_class.distinct().label('grad_class'))
    grad_classes = [row.grad_class for row in grad_classes_query.all()]

    # Get inventory
    inventory = Item.query.order_by(Item.name.asc()).all()

    # Get favorite items
    favorite_inventory = Item.query.filter_by(is_favorite=True).order_by(Item.name.asc()).all()

    # Get quick access item
    quick_access_item = Item.query.filter_by(id=current_app.config['QUICK_ACCESS_ITEM_ID']).first()

    # Sort users alphabetically
    if sort == 'asc':
        users = User.query.filter_by(grad_class=grad_class).order_by(User.last_name.asc()).paginate(page,
            current_app.config['USERS_PER_PAGE'], True)
    else:
        users = User.query.filter_by(grad_class=grad_class).order_by(User.last_name.desc()).paginate(page,
            current_app.config['USERS_PER_PAGE'], True)

    return render_template('index.html.j2', title='Checkout',
                            users=users, sort=sort, inventory=inventory,
                            favorite_inventory=favorite_inventory,
                            quick_access_item=quick_access_item,
                            grad_class=grad_class, grad_classes=grad_classes)

@bp.route('/search')
@login_required
def search():
    """ View search page. """
    if not current_user.is_bartender:
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.index'))
    if not g.search_form.validate():
        return redirect(url_for('main.index'))

    # Get arguments
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'asc', type=str)

    # Get inventory
    inventory = Item.query.order_by(Item.name.asc()).all()

    # Get favorite items
    favorite_inventory = Item.query.filter_by(is_favorite=True).order_by(Item.name.asc()).all()

    # Get quick access item
    quick_access_item = Item.query.filter_by(id=current_app.config['QUICK_ACCESS_ITEM_ID']).first()

    # Get users corresponding to the query
    query_text = g.search_form.q.data
    username_query = User.query.filter(User.username.ilike('%'+query_text+'%'))
    nickname_query = User.query.filter(User.nickname.ilike('%'+query_text+'%'))
    first_name_query = User.query.filter(User.first_name.ilike('%'+query_text+'%'))
    last_name_query = User.query.filter(User.last_name.ilike('%'+query_text+'%'))
    final_query = username_query.union(first_name_query).union(last_name_query).union(nickname_query)
    total = final_query.count()

    # Sort users alphabetically
    if sort == 'asc':
        users = final_query.order_by(User.last_name.asc()).paginate(page,
            current_app.config['USERS_PER_PAGE'], True)
    else:
        users = final_query.order_by(User.last_name.desc()).paginate(page,
            current_app.config['USERS_PER_PAGE'], True)

    # If only one user, redirect to his profile
    if total == 1:
        return redirect(url_for('main.user', username=users.items[0].username))

    return render_template('search.html.j2', title='Search', users=users,
                            sort=sort, inventory=inventory, total=total,
                            favorite_inventory=favorite_inventory,
                            quick_access_item=quick_access_item)

@bp.route('/user/<username>')
@login_required
def user(username):
    """ View user profile page. """
    if current_user.username != username and (not current_user.is_bartender):
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.index'))

    # Get user
    user = User.query.filter_by(username=username).first_or_404()

    today = datetime.date.today()
    age = today.year - user.birthdate.year - \
        ((today.month, today.day) < (user.birthdate.month, user.birthdate.day))

    # Get transactions statistics
    transaction_paid = user.transactions.filter_by(is_reverted=False).filter(Transaction.type.like('Pay%')).all()
    amount_paid = sum([abs(t.balance_change) for t in transaction_paid])
    transactions_top_up = user.transactions.filter_by(is_reverted=False).filter(Transaction.type == 'Top up').all()
    amount_topped_up = sum([abs(t.balance_change) for t in transactions_top_up])

    # Get inventory
    inventory = Item.query.order_by(Item.name.asc()).all()

    # Get favorite items
    favorite_inventory = Item.query.filter_by(is_favorite=True).order_by(Item.name.asc()).all()

    # Get quick access item
    quick_access_item = Item.query.filter_by(id=current_app.config['QUICK_ACCESS_ITEM_ID']).first()

    # Check if user is an admin
    is_admin = user.email in current_app.config['ADMINS']

    return render_template('user.html.j2', title=username + ' profile',
                            age=age, is_admin=is_admin, user=user,
                            inventory=inventory, amount_paid=amount_paid,
                            favorite_inventory=favorite_inventory,
                            quick_access_item=quick_access_item,
                            amount_topped_up=amount_topped_up)

@bp.route('/edit_profile/<username>', methods=['GET', 'POST'])
@fresh_login_required
def edit_profile(username):
    """ Edit user. """
    if not current_user.is_bartender:
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.index'))

    user = User.query.filter_by(username=username).first_or_404()
    form = EditProfileForm(user.email)
    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.birthdate = form.birthdate.data
        user.nickname = form.nickname.data
        user.email = form.email.data
        user.is_bartender = form.is_bartender.data
        if (form.password.data != ''):
            user.set_password(form.password.data)
        db.session.commit()
        flash('Your changes have been saved.', 'success')
        return redirect(url_for('main.user', username=user.username))
    elif request.method == 'GET':
        form.first_name.data = user.first_name
        form.last_name.data = user.last_name
        form.birthdate.data = user.birthdate
        form.nickname.data = user.nickname
        form.email.data = user.email
        form.is_bartender.data = user.is_bartender
    return render_template('edit_profile.html.j2', title='Edit profile',
                           form=form)

@bp.route('/deposit', methods=['GET'])
@login_required
def deposit():
    if not current_user.is_bartender:
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.index'))

    username = request.args.get('username', None, type=str)
    user = User.query.filter_by(username=username).first_or_404()

    if user.deposit == True:
        flash('User already gave a deposit.', 'warning')
        return redirect(request.referrer)

    user.deposit = True
    db.session.commit()

    return redirect(request.referrer)


@bp.route('/delete_user/<username>')
@fresh_login_required
def delete_user(username):
    """ Delete user. """
    if not current_user.is_bartender:
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.index'))

    user = User.query.filter_by(username=username).first_or_404()
    db.session.delete(user)
    db.session.commit()
    flash('The user ' + username + ' has been deleted.', 'success')
    return redirect(url_for('main.index'))

def month_year_iter( start_month, start_year, end_month, end_year ):
    ym_start= 12*start_year + start_month - 1
    ym_end= 12*end_year + end_month - 1
    for ym in range(ym_start, ym_end):
        y, m = divmod(ym, 12)
        yield y, m+1

@bp.route('/statistics')
@login_required
def statistics():
    """ View statistics page. """
    if not current_user.is_bartender:
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.index'))

    month_dict = {
        1:  'January',
        2:  'February',
        3:  'March',
        4:  'April',
        5:  'May',
        6:  'June',
        7:  'July',
        8:  'August',
        9:  'September',
        10: 'October',
        11: 'November',
        12: 'December'
        }

    # Number of clients
    nb_users = User.query.count()
    # Number of bartenders
    nb_bartenders = User.query.filter_by(is_bartender=True).count()
    # Number of active users
    nb_active_users = User.query.filter(User.transactions.any(Transaction.date > datetime.datetime.utcnow() - datetime.timedelta(days=current_app.config['DAYS_BEFORE_INACTIVE']))).count()

    # Get last 12 months range
    current_year = datetime.date.today().year
    current_month = datetime.date.today().month
    if current_month == 12:
        previous_year = current_year
    else:
        previous_year = current_year - 1
    previous_month = (current_month-12) % 12

    # Get money spent and topped up last 12 months
    paid_per_month = []
    topped_per_month = []
    for (y, m) in month_year_iter(previous_month+1, previous_year, current_month+1, current_year):
        transactions_paid_y = Transaction.query.filter(and_(extract('month', Transaction.date) == m, extract('year', Transaction.date) == y)).filter(Transaction.type.like('Pay%')).filter_by(is_reverted=False).all()
        transactions_topped_y = Transaction.query.filter(and_(extract('month', Transaction.date) == m, extract('year', Transaction.date) == y)).filter(Transaction.type.like('Top up')).filter_by(is_reverted=False).all()
        paid_per_month.append(0)
        for t in transactions_paid_y:
            paid_per_month[-1] -= t.balance_change
        topped_per_month.append(0)
        for t in transactions_topped_y:
            topped_per_month[-1] += t.balance_change

    # Generate months labels
    months_labels = ['%.2d' % m[1] + '/'+str(m[0]) for m in list(month_year_iter(previous_month+1, previous_year, current_month+1, current_year))]

    # Get money spent and topped up this month
    paid_this_month = []
    topped_this_month = []
    for day in range(1, monthrange(current_year, current_month)[1] + 1):
        transactions_paid_m = Transaction.query.filter(and_(extract('day', Transaction.date) == day, and_(extract('month', Transaction.date) == m, extract('year', Transaction.date) == y))).filter(Transaction.type.like('Pay%')).filter_by(is_reverted=False).all()
        transactions_topped_m = Transaction.query.filter(and_(extract('day', Transaction.date) == day, and_(extract('month', Transaction.date) == m, extract('year', Transaction.date) == y))).filter(Transaction.type.like('Top up')).filter_by(is_reverted=False).all()
        paid_this_month.append(0)
        for t in transactions_paid_m:
            paid_this_month[-1] -= t.balance_change
        topped_this_month.append(0)
        for t in transactions_topped_m:
            topped_this_month[-1] += t.balance_change
    print(topped_this_month)

    # Generate days labels
    days_labels = ['%.2d' % current_month + '/' + '%.2d' % day for day in range(1, monthrange(current_year, current_month)[1] + 1)]


    # Number of transactions
    nb_transactions = Transaction.query.count()
    # Amount of money paid
    transactions_paid = Transaction.query.filter_by(is_reverted=False).filter(Transaction.type.like('Pay%')).all()
    amount_paid = sum([abs(t.balance_change) for t in transactions_paid])

    return render_template('statistics.html.j2', title='Statistics',
                            nb_users=nb_users, nb_active_users=nb_active_users,
                            nb_bartenders=nb_bartenders,
                            paid_per_month=paid_per_month,
                            topped_per_month=topped_per_month,
                            months_labels=months_labels,
                            paid_this_month=paid_this_month,
                            topped_this_month=topped_this_month,
                            days_labels=days_labels)

@bp.route('/transactions')
@login_required
def transactions():
    """ View transactions page. """
    if not current_user.is_bartender:
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.index'))

    # Get arguments
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'desc', type=str)

    # Sort transactions alphabetically
    if sort == 'asc':
        transactions = Transaction.query.order_by(Transaction.id.asc()).paginate(page,
            current_app.config['ITEMS_PER_PAGE'], True)
    else:
        transactions = Transaction.query.order_by(Transaction.id.desc()).paginate(page,
            current_app.config['ITEMS_PER_PAGE'], True)

    return render_template('transactions.html.j2', title='Transactions',
        transactions=transactions, sort=sort)

@bp.route('/revert_transaction')
@login_required
def revert_transaction():
    """ Delete item from the inventory. """
    if not current_user.is_bartender:
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.index'))

    transaction_id = request.args.get('transaction_id', -1, type=int)

    # Transactions that are already reverted can't be reverted again
    transaction = Transaction.query.filter_by(id=transaction_id).first_or_404()
    if transaction.is_reverted or 'Revert' in transaction.type:
        flash("You can't revert this transaction.", 'warning')
        return redirect(request.referrer)

    # Revert client balance
    if transaction.client:
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

    flash('The transaction #'+str(transaction_id)+' has been reverted.', 'success')
    return redirect(request.referrer)

@bp.route('/inventory')
@login_required
def inventory():
    """View inventory page.
    """
    if not current_user.is_bartender:
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.index'))

    # Get arguments
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'asc', type=str)

    # Get quick access item
    quick_access_item = Item.query.filter_by(id=current_app.config['QUICK_ACCESS_ITEM_ID']).first_or_404()

    # Sort items alphabetically
    if sort == 'asc':
        inventory = Item.query.order_by(Item.name.asc()).paginate(page,
            current_app.config['ITEMS_PER_PAGE'], True)
    else:
        inventory = Item.query.order_by(Item.name.desc()).paginate(page,
            current_app.config['ITEMS_PER_PAGE'], True)

    return render_template('inventory.html.j2', title='Inventory',
        inventory=inventory, sort=sort, quick_access_item=quick_access_item)

@bp.route('/set_quick_access_item/<item_name>')
@login_required
def set_quick_access_item(item_name):
    """Set the quick acces item.
    """
    if not current_user.is_bartender:
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.index'))

    # Get item
    item = Item.query.filter_by(name=item_name).first_or_404()

    # Get current quick access item
    quick_access_item = GlobalSetting.query.filter_by(key='QUICK_ACCESS_ITEM_ID').first_or_404()

    # Update the quick access item
    current_app.config['QUICK_ACCESS_ITEM_ID'] = item.id
    quick_access_item.value = item.id
    db.session.commit()

    return redirect(request.referrer)


@bp.route('/add_item', methods=['GET', 'POST'])
@login_required
def add_item():
    """ Add item. """
    if not current_user.is_bartender:
        flash("You don't have the rights to acces this page.", 'danger')
        return redirect(url_for('main.index'))

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
        flash('The item '+item.name+' was successfully added.', 'success')
        return redirect(url_for('main.inventory'))
    return render_template('add_item.html.j2', title='Add item', form=form)

@bp.route('/edit_item/<item_name>', methods=['GET', 'POST'])
@fresh_login_required
def edit_item(item_name):
    """ Edit item. """
    if not current_user.is_bartender:
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.index'))

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
        flash('Your changes have been saved.', 'success')
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

    return redirect(request.referrer)

@bp.route('/delete_item')
@login_required
def delete_item():
    """ Delete item from the inventory. """
    if not current_user.is_bartender:
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.index'))

    item_name = request.args.get('item_name', 'none', type=str)

    item = Item.query.filter_by(name=item_name).first_or_404()
    db.session.delete(item)
    db.session.commit()
    flash('The item ' + item_name + ' has been deleted.', 'success')
    return redirect(request.referrer)

@bp.route('/top_up', methods=['GET', 'POST'])
@login_required
def top_up():
    """ Top up user and redirect to last page. """
    if not current_user.is_bartender:
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.index'))

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

    flash('You added ' + str(amount) + '€ to ' + user.first_name + ' ' + \
            user.last_name + "'s account.", 'info')
    return redirect(request.referrer)

@bp.route('/pay', methods=['GET', 'POST'])
@login_required
def pay():
    """ Substract the item price to username's balance. """
    if not current_user.is_bartender:
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.index'))

    username = request.args.get('username', 'none', type=str)
    item_name = request.args.get('item_name', 'none', type=str)

    user = User.query.filter_by(username=username).first_or_404()
    item = Item.query.filter_by(name=item_name).first_or_404()

    if not user.deposit:
        flask(user.username+" hasn't given a deposit.", 'warning')
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
                            date=datetime.datetime.utcnow(), type='Pay '+item.name,
                            balance_change=-item.price)
    db.session.add(transaction)
    db.session.commit()

    flash(user.username+' successfully bought '+item.name + \
        '. Balance: {:.2f}'.format(user.balance)+'€', 'success')
    return redirect(request.referrer)

@bp.route('/scanqrcode')
@login_required
def scanqrcode():
    """ QR code scan to easily find a user. """
    if not current_user.is_bartender:
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.index'))

    return render_template('scanqrcode.html.j2', title='Scan QR code')

@bp.route('/get_user_from_qr')
@login_required
def get_user_from_qr():
    """ The QR code scanner redirects to this page when a QR code is scanned.
        The corresponding user is retrieved and this page redirects to the
        user's profile. """
    if not current_user.is_bartender:
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.index'))

    # Get arguments
    qrcode_hash = request.args.get('qrcode_hash', 'None', type=str)

    # Retrieve corresponding user
    user = User.query.filter_by(qrcode_hash=qrcode_hash).first_or_404()

    return redirect(url_for('main.user', username=user.username))

@bp.route('/qrcode/<username>')
@login_required
def qrcode(username):
    """ View user's QR code. """
    if current_user.username != username and (not current_user.is_bartender):
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.index'))

    user = User.query.filter_by(username=username).first_or_404()

    return render_template('qrcode.html.j2', title='QR code', user=user)

@bp.route('/global_settings', methods=['GET', 'POST'])
@login_required
def global_settings():
    """ Set global web app settings. """
    if not current_user.is_bartender:
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.index'))

    form = GlobalSettingsForm()
    if form.validate_on_submit():
        settings = GlobalSetting.query.all()
        for index, s in enumerate(settings):
            s.value = form.value.data[index]
            current_app.config[s.key] = s.value
        db.session.commit()
        flash('Global settings successfully updated.', 'success')
        return redirect(url_for('main.global_settings'))
    else:
        settings = GlobalSetting.query.all()
        for index, s in enumerate(settings):
            form.value.append_entry(s.value)
            form.value.entries[index].label.text = s.name
    return render_template('global_settings.html.j2', title='Global settings', form=form)
