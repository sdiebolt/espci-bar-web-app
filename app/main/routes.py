from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from app import db
from app.main.forms import EditProfileForm
from app.models import User
from app.main import bp


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    if not current_user.is_barman:
        return redirect(url_for('main.user', username=current_user.username))
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.last_name.asc()).paginate(page,
        current_app.config['USERS_PER_PAGE'], False)
    next_url = url_for('main.index', page=users.next_num) \
        if users.has_next else None
    prev_url = url_for('main.index', page=users.prev_num) \
        if users.has_prev else None
    return render_template('index.html.j2', title='Home Page',
                            users=users.items, next_url=next_url,
                            prev_url=prev_url)

@bp.route('/user/<username>')
@login_required
def user(username):
    if current_user.username != username and (not current_user.is_barman):
        flash("You don't have the rights to view this profile.", 'danger')
        return redirect(url_for('main.user', username=current_user.username))
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html.j2', user=user)

@bp.route('/edit_profile/<username>', methods=['GET', 'POST'])
@login_required
def edit_profile(username):
    if current_user.username != username and (not current_user.is_barman):
        flash("You don't have the rights to modify this profile.", 'danger')
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
    return render_template('edit_profile.html.j2', title='Edit Profile',
                           form=form)

@bp.route('/delete_user/<username>')
@login_required
def delete_user(username):
    if not current_user.is_barman:
        flash("You don't have the rights to delete this user.", 'danger')
        return redirect(url_for('main.index'))
    user = User.query.filter_by(username=username).first_or_404()
    db.session.delete(user)
    db.session.commit()
    flash('The user ' + username + ' has been deleted.', 'success')
    return redirect(url_for('main.index'))
