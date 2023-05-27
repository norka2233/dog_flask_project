from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import DogUser


class LoginForm(FlaskForm):
    dog_name = StringField('Dog Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    dog_name = StringField('Dog_name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_dog_name(self, dog_name):
        dog_user = DogUser.query.filter_by(dog_name=dog_name.data).first()
        if dog_user is not None:
            raise ValidationError('This dog_username is not correct.')

    def validate_email(self, email):
        dog_user = DogUser.query.filter_by(email=email.data).first()
        if dog_user is not None:
            raise ValidationError('This email is not correct.')


class EditProfileForm(FlaskForm):
    dog_name = StringField('Dog_name', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_dog_name, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_dog_name = original_dog_name

    def validate_dog_name(self, dog_name):
        if dog_name.data != self.original_dog_name:
            dog_user = DogUser.query.filter_by(dog_name=self.dog_name.data).first()
            if dog_user is not None:
                raise ValidationError('Please use a different Dog name.')


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')

