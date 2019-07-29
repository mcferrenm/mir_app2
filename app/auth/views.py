from flask import request
from flask_login import login_user, logout_user, login_required
from . import auth
from ..models import User


@auth.route('/login', methods=['GET', 'POST'])
def login():
    req = request.get_json()
    user = User.query.filter_by(email=req['email']).first()
    if user is not None and user.verify_password(req['password']):
        login_user(user, req['remember_me'])  # remember me True
        return '<h1>Hello {}</h1>'.format(user.username)
    else:
        # TODO(max): set status code 404
        return '<h1>User not found</h1>'


@auth.route('/logout')
@login_required
def logout():
    logout_user()
