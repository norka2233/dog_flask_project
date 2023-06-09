from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.urls import url_parse
from flask_babel import _, get_locale
from app import app, db
from app.authentication.email import send_password_reset_email
from app.authentication.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm, PostForm, ResetPasswordRequestForm, ResetPasswordForm
from app.models import DogUser, Post
from app.translate import translate
from langdetect import detect, LangDetectException


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale =str(get_locale())


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        try:
            language = detect(form.post.data)
        except LangDetectException:
            language = ''
        post = Post(body=form.post.data, author=current_user,
                    language=language)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title=_('Homepage'), form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        dog_user = DogUser.query.filter_by(dog_name=form.dog_name.data).first()
        if dog_user is None or not dog_user.check_password(form.password.data):
            flash(_('Invalid username or password'))
            return redirect(url_for('login'))
        login_user(dog_user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title=_('Sign In'), form=form)


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
        flash(_('Congrats, the dog_user is registered now!'))
        return redirect(url_for('login'))
    return render_template('register.html', title=_('Register'), form=form)


@app.route('/user/<dog_name>')
@login_required
def dog_user(dog_name):
    # from pdb import set_trace
    # set_trace()
    dog_user = DogUser.query.filter_by(dog_name=dog_name).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = dog_user.posts.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('dog_user', dog_name=dog_user.dog_name, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('dog_user', dog_name=dog_user.dog_name, page=posts.prev_num) \
        if posts.has_prev else None
    form = EmptyForm()
    return render_template('dog_user.html', dog_user=dog_user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url, form=form)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.dog_name)
    if form.validate_on_submit():
        current_user.dog_name = form.dog_name.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.dog_name.data = current_user.dog_name
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'), form=form)


@app.route('/follow/<dog_name>', methods=['POST'])
@login_required
def follow(dog_name):
    form = EmptyForm()
    if form.validate_on_submit():
        dog_user = DogUser.query.filter_by(dog_name=dog_name).first()
        if dog_user is None:
            flash(_(f'Dog user %{dog_name}s not found.', dog_name=dog_name))
            return redirect(url_for('index'))
        if dog_user == current_user:
            flash(_('You cannot follow yourself!'))
            return redirect(url_for('dog_user', dog_name=dog_name))
        current_user.follow(dog_user)
        db.session.commit()
        flash(_(f'You are following %{dog_name}s now.', dog_name=dog_name))
        return redirect(url_for('dog_user', dog_name=dog_name))
    else:
        return redirect(url_for('index'))


@app.route('/unfollow/<dog_name>', methods=['POST'])
@login_required
def unfollow(dog_name):
    form = EmptyForm()
    if form.validate_on_submit():
        dog_user = DogUser.query.filter_by(dog_name=dog_name).first()
        if dog_user is None:
            flash(_(f'Dog user %{dog_name}s not found.', dog_name=dog_name))
            return redirect(url_for('index'))
        if dog_user == current_user:
            flash(_('You cannot unfollow yourself!'))
            return redirect(url_for('dog_user', dog_name=dog_name))
        current_user.unfollow(dog_user)
        db.session.commit()
        flash(_(f'You are not following %{dog_name}s anymore.,', dog_name=dog_name))
        return redirect(url_for('dog_user', dog_name=dog_name))
    else:
        return redirect(url_for('index'))


@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.prev_num else None
    return render_template('index.html', title=_('Explore'), posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        dog_user = DogUser.query.filter_by(email=form.email.data).first()
        if dog_user:
            send_password_reset_email(dog_user)
        flash(_('Check your email for the instructions to reset your password'))
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', title=_('Reset Password'), form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    dog_user = DogUser.verify_reset_password_token(token)
    if not dog_user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        dog_user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


@app.route('/translate', methods=['POST'])
@login_required
def translate_text():
    return jsonify({'text': translate(request.form['text'],
                                      request.form['source_language'],
                                      request.form['dest_language'])})