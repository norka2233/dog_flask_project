from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from langdetect import detect, LangDetectException
from app import db
from app.main.forms import EditProfileForm, EmptyForm, PostForm
from app.models import DogUser, Post
from app.translate import translate
from app.main import bp


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale =str(get_locale())


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
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
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('main.index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title=_('Homepage'), form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('main.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) \
        if posts.prev_num else None
    return render_template('index.html', title=_('Explore'), posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/user/<dog_name>')
@login_required
def dog_user(dog_name):
    dog_user = DogUser.query.filter_by(dog_name=dog_name).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = dog_user.posts.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('dog_user', dog_name=dog_user.dog_name, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('dog_user', dog_name=dog_user.dog_name, page=posts.prev_num) \
        if posts.has_prev else None
    form = EmptyForm()
    return render_template('dog_user.html', dog_user=dog_user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url, form=form)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.dog_name)
    if form.validate_on_submit():
        current_user.dog_name = form.dog_name.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.dog_name.data = current_user.dog_name
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'), form=form)


@bp.route('/follow/<dog_name>', methods=['POST'])
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
        return redirect(url_for('main.dog_user', dog_name=dog_name))
    else:
        return redirect(url_for('main.index'))


@bp.route('/unfollow/<dog_name>', methods=['POST'])
@login_required
def unfollow(dog_name):
    form = EmptyForm()
    if form.validate_on_submit():
        dog_user = DogUser.query.filter_by(dog_name=dog_name).first()
        if dog_user is None:
            flash(_(f'Dog user %{dog_name}s not found.', dog_name=dog_name))
            return redirect(url_for('main.index'))
        if dog_user == current_user:
            flash(_('You cannot unfollow yourself!'))
            return redirect(url_for('main.dog_user', dog_name=dog_name))
        current_user.unfollow(dog_user)
        db.session.commit()
        flash(_(f'You are not following %{dog_name}s anymore.,', dog_name=dog_name))
        return redirect(url_for('main.dog_user', dog_name=dog_name))
    else:
        return redirect(url_for('main.index'))


@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    return jsonify({'text': translate(request.form['text'],
                                      request.form['source_language'],
                                      request.form['dest_language'])})