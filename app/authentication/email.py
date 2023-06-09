# from flask_mail import Message
from flask import current_app, render_template
from flask_babel import _
from app.email import send_email


def send_password_reset_email(dog_user):
    token = dog_user.get_reset_password_token()
    send_email(_('[DogFlaskProject] Reset Your Password'),
               sender=current_app.config['ADMINS'][0],
               recipients=[dog_user.email],
               text_body=render_template('email/reset_password.txt',
                                         dog_user=dog_user, token=token),
               html_body=render_template('email/reset_password.html',
                                         dog_user=dog_user, token=token))