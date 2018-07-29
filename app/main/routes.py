from datetime import datetime, timedelta
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from app import db
from app.main.forms import EditProfileForm, EditItemForm, AddItemForm
from app.models import User, Item
from app.main import bp


@bp.route('/', methods=['GET'])
@bp.route('/index', methods=['GET'])
@login_required
def index():
    """ View index page. For barmen, it's the customers page and for clients,
        it redirects to the profile. """
    if not current_user.is_barman:
        return redirect(url_for('main.user', username=current_user.username))

    # Get arguments
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'asc', type=str)
    grad_class = request.args.get('grad_class', str(current_app.config['CURRENT_GRAD_CLASS']), type=int)

    # Get graduating classes from database
    grad_classes_query = db.session.query(User.grad_class.distinct().label('grad_class'))
    grad_classes = [row.grad_class for row in grad_classes_query.all()]

    # Sort users alphabetically
    if sort == 'asc':
        users = User.query.filter_by(grad_class=grad_class).order_by(User.last_name.asc()).paginate(page,
            current_app.config['USERS_PER_PAGE'], True)
    else:
        users = User.query.filter_by(grad_class=grad_class).order_by(User.last_name.desc()).paginate(page,
            current_app.config['USERS_PER_PAGE'], True)

    # Get inventory
    inventory = Item.query.order_by(Item.name.asc()).all()

    return render_template('index.html.j2', title='Home page',
                            users=users, sort=sort, inventory=inventory,
                            grad_class=grad_class, grad_classes=grad_classes)

@bp.route('/user/<username>')
@login_required
def user(username):
    """ View user profile page. """
    if current_user.username != username and (not current_user.is_barman):
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.user', username=current_user.username))

    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html.j2', title=username + ' profile',
        user=user)

@bp.route('/edit_profile/<username>', methods=['GET', 'POST'])
@login_required
def edit_profile(username):
    """ Edit user. """
    if current_user.username != username and (not current_user.is_barman):
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.index'))

    user = User.query.filter_by(username=username).first_or_404()
    form = EditProfileForm(user.email)
    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data
        if (form.password.data != ''):
            user.set_password(form.password.data)
        db.session.commit()
        flash('Your changes have been saved.', 'success')
        return redirect(url_for('main.user', username=user.username))
    elif request.method == 'GET':
        form.first_name.data = user.first_name
        form.last_name.data = user.last_name
        form.email.data = user.email
    return render_template('edit_profile.html.j2', title='Edit profile',
                           form=form)

@bp.route('/delete_user/<username>')
@login_required
def delete_user(username):
    """ Delete user. """
    if not current_user.is_barman:
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.index'))

    user = User.query.filter_by(username=username).first_or_404()
    db.session.delete(user)
    db.session.commit()
    flash('The user ' + username + ' has been deleted.', 'success')
    return redirect(url_for('main.index'))


@bp.route('/top_up/<username>', methods=['GET', 'POST'])
@login_required
def top_up(username):
    """ Top up user and redirect to last page. """
    if not current_user.is_barman:
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.index'))

    try:
        amount = float(request.form.get('amount', 0, type=str))
    except ValueError:
        flash('Please enter a numerical value.', 'warning')
        return redirect(request.referrer)

    if amount < 0:
        flash('Please enter a positive value.', 'warning')
        return redirect(request.referrer)

    user = User.query.filter_by(username=username).first_or_404()
    user.balance += amount
    db.session.commit()

    flash('You added ' + str(amount) + '€ to ' + user.first_name + ' ' + \
            user.last_name + "'s account.", 'info')
    return redirect(request.referrer)

@bp.route('/statistics')
@login_required
def statistics():
    """ View statistics page. """
    if not current_user.is_barman:
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.index'))

    # Number of clients
    nb_users = User.query.count()
    # Number of bartenders
    nb_bartenders = User.query.filter_by(is_barman=True).count()
    # Number of active users
    nb_active_users = User.query.filter(User.last_drink > (datetime.today() - timedelta(days=30))).count()
    return render_template('statistics.html.j2', title='Statistics',
                            nb_users=nb_users, nb_active_users=nb_active_users,
                            nb_bartenders=nb_bartenders)

@bp.route('/inventory')
@login_required
def inventory():
    """ View inventory page. """
    if not current_user.is_barman:
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.index'))

    # Get arguments
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'asc', type=str)

    # Sort items alphabetically
    if sort == 'asc':
        inventory = Item.query.order_by(Item.name.asc()).paginate(page,
            current_app.config['ITEMS_PER_PAGE'], True)
    else:
        inventory = Item.query.order_by(Item.name.desc()).paginate(page,
            current_app.config['ITEMS_PER_PAGE'], True)

    return render_template('inventory.html.j2', title='Home page',
        inventory=inventory, sort=sort)

@bp.route('/add_item', methods=['GET', 'POST'])
@login_required
def add_item():
    """ Add item. """
    if not current_user.is_barman:
        flash("You don't have the rights to acces this page.", 'danger')
        return redirect(url_for('main.index'))

    form = AddItemForm()
    if form.validate_on_submit():
        quantity = form.quantity.data
        if quantity is None:
            quantity = 0
        item = Item(name=form.name.data, quantity=quantity,
                    price=form.price.data, is_alcohol=form.is_alcohol.data)
        db.session.add(item)
        db.session.commit()
        flash('The item '+item.name+' was successfully added.', 'success')
        return redirect(url_for('main.inventory'))
    return render_template('add_item.html.j2', title='Add item', form=form)

@bp.route('/edit_item/<item_name>', methods=['GET', 'POST'])
@login_required
def edit_item(item_name):
    """ Edit item. """
    if not current_user.is_barman:
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.index'))

    item = Item.query.filter_by(name=item_name).first_or_404()
    form = EditItemForm(item.name)
    if form.validate_on_submit():
        quantity = form.quantity.data
        if quantity is None:
            quantity = 0
        item.name = form.name.data
        item.quantity = quantity
        item.price = form.price.data
        item.is_alcohol = form.is_alcohol.data
        db.session.commit()
        flash('Your changes have been saved.', 'success')
        return redirect(url_for('main.inventory'))
    elif request.method == 'GET':
        form.name.data = item.name
        form.quantity.data = item.quantity
        form.price.data = item.price
        form.is_alcohol.data = item.is_alcohol
    return render_template('edit_item.html.j2', title='Edit item',
                           form=form)

    return redirect(request.referrer)

@bp.route('/delete_item/<item_name>')
@login_required
def delete_item(item_name):
    """ Delete item from the inventory. """
    if not current_user.is_barman:
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.index'))

    item = Item.query.filter_by(name=item_name).first_or_404()
    db.session.delete(item)
    db.session.commit()
    flash('The item ' + item_name + ' has been deleted.', 'success')
    return redirect(request.referrer)
