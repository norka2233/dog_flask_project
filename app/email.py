from flask_mail import Message
from app import app, mail
from flask import render_template


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)


def send_password_reset_email(dog_user):
    token = dog_user.get_reset_password_token()
    send_email('[DogFlaskProject] Reset Your Password',
               sender=app.config['ADMINS'][0],
               recipients=[dog_user.email],
               text_body=render_template('email/reset_password.txt',
                                         dog_user=dog_user, token=token),
               html_body=render_template('email/reset_password.html',
                                         dog_user=dog_user, token=token))