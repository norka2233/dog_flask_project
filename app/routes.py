from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from app.models import DogUser


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/')
@app.route('/index')
@login_required
def index():
    dog_user = {'username': 'Shnurok'}
    posts = [
        {
            'author': {'username': 'Groshyk'},
            'body': 'Hi everyone!'
        },
        {
            'author': {'username': 'Shkedryk'},
            'body': 'Hi dogs!'
        }
    ]
    return render_template('index.html', title='Homepage', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        dog_user = DogUser.query.filter_by(dog_name=form.dog_name.data).first()
        if dog_user is None or not dog_user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(dog_user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        dog_user = DogUser(dog_name=form.dog_name.data, email=form.email.data)
        dog_user.set_password(form.password.data)
        db.session.add(dog_user)
        db.session.commit()
        flash('Congrats, the dog_user is registered now!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<dog_name>')
@login_required
def dog_user(dog_name):
    # from pdb import set_trace
    # set_trace()
    dog_user = DogUser.query.filter_by(dog_name=dog_name).first_or_404()
    posts = [
        {'author': dog_user, 'body': 'Test post #1'},
        {'author': dog_user, 'body': 'Test post #2'}
    ]
    return render_template('dog_user.html', dog_user=dog_user, posts=posts)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.dog_name = form.dog_name.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.dog_name.data = current_user.dog_name
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)
