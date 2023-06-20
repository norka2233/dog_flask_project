from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, current_user, logout_user
from flask_babel import _
from app import db
from app.authentication import bp
from app.authentication.forms import LoginForm, RegistrationForm, \
    ResetPasswordRequestForm, ResetPasswordForm
from app.models import DogUser
from app.authentication.email import send_password_reset_email


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        dog_user = DogUser.query.filter_by(dog_name=form.dog_name.data).first()
        if dog_user is None or not dog_user.check_password(form.password.data):
            flash(_('Invalid username or password'))
            return redirect(url_for('auth.login'))
        login_user(dog_user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('authentication/login.html', title=_('Sign In'), form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        dog_user = DogUser(dog_name=form.dog_name.data, email=form.email.data)
        dog_user.set_password(form.password.data)
        db.session.add(dog_user)
        db.session.commit()
        flash(_('Congrats, the dog_user is registered now!'))
        return redirect(url_for('auth.login'))
    return render_template('authentication/register.html', title=_('Register'), form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        dog_user = DogUser.query.filter_by(email=form.email.data).first()
        if dog_user:
            send_password_reset_email(dog_user)
        flash(_('Check your email for the instructions to reset your password'))
        return redirect(url_for('authentication.login'))
    return render_template('authentication/reset_password_request.html', title=_('Reset Password'), form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    dog_user = DogUser.verify_reset_password_token(token)
    if not dog_user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        dog_user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('authentication.login'))
    return render_template('authentication/reset_password.html', form=form)