from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user, \
    login_required, fresh_login_required
from app import db, login
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, \
    ResetPasswordRequestForm, ResetPasswordForm
from app.models import User
from app.auth.email import send_password_reset_email


@login.needs_refresh_handler
@login_required
def refresh():
    logout_user()
    flash('To protect your account, please reauthenticate to access this '
        'page.', 'warning')
    return redirect(url_for('auth.login'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash("You can't access this page while being logged in.", 'danger')
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        flash('You were successfully logged in.', 'success')
        return redirect(next_page)
    return render_template('auth/login.html.j2', title='Sign In', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You were successfully logged out.', 'success')
    return redirect(url_for('auth.login'))

@bp.route('/register', methods=['GET', 'POST'])
@fresh_login_required
def register():
    if not current_user.is_bartender:
        flash("You don't have the rights to access this page.", 'danger')
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        grad_class = form.grad_class.data
        if grad_class is None:
            grad_class = 0
        user = User(first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    birthdate=form.birthdate.data,
                    grad_class=form.grad_class.data,
                    username=form.username.data, email=form.email.data,
                    is_bartender=form.is_bartender.data)
        user.set_password(form.password.data)
        user.set_qrcode()
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, the user '+user.username+' has been added.',
                'success')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html.j2', title='Register',
                            form=form)

@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        flash("You can't access this page while being logged in.", 'danger')
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password.',
                'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html.j2',
                            title='Reset Password', form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        flash("You can't access this page while being logged in.", 'danger')
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html.j2', form=form)
