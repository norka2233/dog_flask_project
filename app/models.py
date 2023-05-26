from datetime import datetime
from hashlib import md5
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app import login


followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('dog_user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('dog_user.id'))
)


class DogUser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dog_name = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship(
        'DogUser', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return f'<Dog User {self.dog_name}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def follow(self, dog_user):
        if not self.is_following(dog_user):
            self.followed.append(dog_user)

    def unfollow(self, dog_user):
        if self.is_following(dog_user):
            self.followed.remove(dog_user)

    def is_following(self, dog_user):
        return self.followed.filter(
            followers.c.followed_id == dog_user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.dog_user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(dog_user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())


@login.user_loader
def load_dog_user(id):
    return DogUser.query.get(int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    dog_user_id = db.Column(db.Integer, db.ForeignKey('dog_user.id'))

    def __repr__(self):
        return f'<Post {self.body}>'



