from flask_mail import Message
from flask import render_template
from threading import Thread
from flask_babel import _
from app import app, mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()


def send_password_reset_email(dog_user):
    token = dog_user.get_reset_password_token()
    send_email(_('[DogFlaskProject] Reset Your Password'),
               sender=app.config['ADMINS'][0],
               recipients=[dog_user.email],
               text_body=render_template('email/reset_password.txt',
                                         dog_user=dog_user, token=token),
               html_body=render_template('email/reset_password.html',
                                         dog_user=dog_user, token=token))