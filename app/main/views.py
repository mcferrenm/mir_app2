from flask import session
from . import main
from .. import db
from ..models import User


@main.route('/<username>', methods=['GET', 'POST'])
def index(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        user = User(username=username)
        db.session.add(user)
        db.session.commit()
        session['known'] = False
    else:
        session['known'] = True
    session['name'] = username
    return '<h1>Ayyy !{}</h1>'.format(session.get('name'))
