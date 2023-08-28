from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from app.models import DogUser
from app.api.errors import error_response

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()


@basic_auth.verify_password
def verify_password(dog_name, password):
    dog_user = DogUser.query.filter_by(dog_name=dog_name).first()
    if dog_user and dog_user.check_password(password):
        return dog_user


@basic_auth.error_handler
def basic_auth_error(status):
    return error_response(status)


@token_auth.verify_token
def verify_token(token):
    return DogUser.check_token(token) if token else None

@token_auth.error_handler
def token_auth_error(status):
    return error_response(status)