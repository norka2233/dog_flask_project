from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm


@app.route('/')
@app.route('/index')
def index():
    dog_user = {'username': 'Shnurok'}
    dog_posts = [
        {
            'author': {'username': 'Groshyk'},
            'body': 'Hi everyone!'
        },
        {
            'author': {'username': 'Shkedryk'},
            'body': 'Hi dogs!'
        }
    ]
    return render_template('index.html', title='Homepage', dog_user=dog_user, dog_posts=dog_posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash(f'Login requested for dog_user {form.dog_name.data}, remember_me={form.remember_me.data}')
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)