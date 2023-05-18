from datetime import datetime
from app import db


class DogUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dog_name = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __repr__(self):
        return f'<Dog User {self.dog_name}>'


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    dog_user_id = db.Column(db.Integer, db.ForeignKey('dog_user.id'))

    def __repr__(self):
        return f'<Post {self.body}>'
