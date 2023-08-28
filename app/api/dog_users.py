from flask import jsonify, request, url_for, abort
from app import db
from app.models import DogUser
from app.api import bp
from app.api.errors import bad_request
from app.api.auth import token_auth


@bp.route('/dog_users/<int:id>', methods=['GET'])
@token_auth.login_required
def get_dog_user(id):
    return jsonify(DogUser.query.get_or_404(id).to_dict())


@bp.route('/dog_users', methods=['GET'])
@token_auth.login_required
def get_dog_users():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = DogUser.to_collection_dict(DogUser.query, page, per_page, 'api.get_dog_users')
    return jsonify(data)


@bp.route('/dog_users/<int:id>/followers', methods=['GET'])
@token_auth.login_required
def get_followers(id):
    dog_user = DogUser.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = DogUser.to_collection_dict(dog_user.followers, page, per_page, 'api.get_followers', id=id)
    return jsonify(data)


@bp.route('/dog_users/<int:id>/followed', methods=['GET'])
@token_auth.login_required
def get_followed(id):
    dog_user = DogUser.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = DogUser.to_collection_dict(dog_user.followed, page, per_page, 'api.get_followed', id=id)
    return jsonify(data)


@bp.route('/dog_users', methods=['POST'])
def create_dog_user():
    data = request.get_json() or {}
    if 'dog_name' not in data or 'email' not in data or 'password' not in data:
        return bad_request('must include dog_name, email and password fields')
    if DogUser.query.filter_by(dog_name=data['dog_name']).first():
        return bad_request('please use a different dog_name')
    if DogUser.query.filter_by(email=data['email']).first():
        return bad_request('please use a different email address')
    dog_user = DogUser()
    dog_user.from_dict(data, new_user=True)
    db.session.add(dog_user)
    db.session.commit()
    response = jsonify(dog_user.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_dog_user', id=dog_user.id)
    return response


@bp.route('/dog_users/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_dog_user(id):
    if token_auth.current_user().id != id:
        abort(403)
    dog_user = DogUser.query.get_or_404(id)
    data = request.get_json() or {}
    if 'dog_name' in data and data['dog_name'] != dog_user.dog_name and \
            DogUser.query.filter_by(dog_name=data['dog_name']).first():
        return bad_request('please use a different dog username')
    if 'email' in data and data['email'] != dog_user.email and \
            DogUser.query.filter_by(email=data['email']).first():
        return bad_request('please use a different email address')
    dog_user.from_dict(data, new_user=False)
    db.session.commit()
    return jsonify(dog_user.to_dict())