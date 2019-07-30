from flask import session, request
from flask_login import login_required, current_user
from . import main
from .. import db
from ..models import User


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return '<h1>Ayyy !{}</h1>'.format(user.username)


@main.route('/edit-profile', methods=['POST'])
@login_required
def edit_profile():
    json_req = request.get_json()
    current_user.name = json_req['name']
    current_user.location = json_req['location']
    current_user.about_me = json_req['about_me']
    db.session.add(current_user._get_current_object())
    db.session.commit()
    # TODO(max): proper JSON responses and error handling / validation
    return '<h1>Updated {}</h1>'.format(current_user.name)
