from flask import request
from flask_login import login_user, logout_user, login_required
from . import auth
from .. import db
from ..models import User


@auth.route('/login', methods=['POST'])
def login():
    json_req = request.get_json()
    user = User.query.filter_by(email=json_req['email']).first()
    if user is not None and user.verify_password(json_req['password']):
        login_user(user, json_req['remember_me'])  # remember me True
        # TODO(max): return json response
        return '<h1>Welcome back {}</h1>'.format(user.username)
    else:
        # TODO(max): set status code 404
        return '<h1>User not found</h1>'


@auth.route('/logout')
@login_required
def logout():
    logout_user()


@auth.route('/register', methods=['POST'])
def register():
    json_req = request.get_json()
    user = User(email=json_req['email'],
                username=json_req['username'],
                password=json_req['password'])
    # TODO(max): What if user already exists?
    db.session.add(user)
    db.session.commit()
    # TODO(max): return json response
    return '<h1>{} is now registered</h1>'.format(user.username)
