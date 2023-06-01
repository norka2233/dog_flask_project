from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from flask_babel import _, lazy_gettext as _l
from app.models import DogUser


class LoginForm(FlaskForm):
    dog_name = StringField(_l('Dog Name'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember Me'))
    submit = SubmitField(_l('Sign In'))


class RegistrationForm(FlaskForm):
    dog_name = StringField(_l('Dog_name'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(_l('Repeat Password'), validators=[DataRequired(),
                                 EqualTo('password')])
    submit = SubmitField(_l('Register'))

    def validate_dog_name(self, dog_name):
        dog_user = DogUser.query.filter_by(dog_name=dog_name.data).first()
        if dog_user is not None:
            raise ValidationError(_('This dog_username is not correct.'))

    def validate_email(self, email):
        dog_user = DogUser.query.filter_by(email=email.data).first()
        if dog_user is not None:
            raise ValidationError(_('This email is not correct.'))


class EditProfileForm(FlaskForm):
    dog_name = StringField(_l('Dog_name'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About me'), validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Submit'))

    def __init__(self, original_dog_name, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_dog_name = original_dog_name

    def validate_dog_name(self, dog_name):
        if dog_name.data != self.original_dog_name:
            dog_user = DogUser.query.filter_by(dog_name=self.dog_name.data).first()
            if dog_user is not None:
                raise ValidationError(_('Please use a different Dog name.'))


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    post = TextAreaField(_l('Say something'), validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField(_l('Submit'))


class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Request Password Reset'))


class ResetPasswordForm(FlaskForm):
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Repeat Password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Request Password Reset'))