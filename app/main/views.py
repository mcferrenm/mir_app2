import os
from flask import session, request, current_app, \
    redirect, url_for, send_from_directory, jsonify, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from . import main
from .. import db
from ..models import User, Role, Permission, Post
from ..decorators import admin_required, permission_required


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return jsonify({"posts": [{"body_text": post.body} for post in posts], "username": user.username, })


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


@main.route('/edit-profile/<int:id>', methods=['POST'])
@login_required
# @admin_required
def edit_profile_admin(id):
    # TODO(max): Should we use both query args and req body?
    # TODO(max): Is there an better way to get json from the req object?
    # TODO(max): Can't change only one attribute, resets all of them!

    user = User.query.get_or_404(id)

    json_req = request.get_json()
    # user.email = json_req.get('email')
    # user.role = Role.query.get(json_req.get('role'))
    # user.name = json_req.get('name')
    # user.location = json_req.get('location')
    user.about_me = json_req.get('about_me')
    db.session.add(user)
    db.session.commit()
    return {
        'message': '{} successfully updated.'
        .format(user.name)
    }


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in \
        current_app.config['ALLOWED_EXTENSIONS']


@main.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            # TODO(max): set failed status code
            return {'error': 'No file Part'}
        file = request.files['file']
        # if user does not select file, browser also
        # submits an empty part without filename
        if file.filename == '':
            return {'error': 'No selected file'}
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(
                current_app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('main.uploaded_file', filename=filename))


@main.route('/uploads/<filename>', methods=['GET'])
def uploaded_file(filename):
    # TODO(max): rewrite relative path correctly with os.path.join
    return send_from_directory('../' + current_app.config['UPLOAD_FOLDER'],
                               filename)


@main.route('/posts', methods=['POST'])
def add_post():
    json_req = request.get_json()
    if 'body_text' not in json_req:
        return {"error": "Post must include body_text field."}
    if current_user.can(Permission.WRITE):
        post = Post(body=json_req['body_text'],
                    author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return {"message": "Post by {} created successfully.".format(post.author.name)}
    return {"error": "Not permitted."}


@main.route('/posts', methods=['GET'])
def get_posts():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.id.desc()).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False
    )
    posts = pagination.items
    return jsonify([{"body_text": post.body,
                     "id": post.id,
                     "username": post.author.username,
                     "author": post.author.name} for post in posts])


@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    # TODO(max): add to_json method to Post Model
    return {"body_text": post.body, "author": post.author.name, "id": post.id}


@main.route('/edit/<int:id>', methods=['POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMIN):
        abort(403)
    json_req = request.get_json()
    print(json_req)
    post.body = json_req["body_text"]
    db.session.add(post)
    db.session.commit()
    return {"body_text": post.body, "author": post.author.name, "id": post.id}


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        return {"error": "Invalid user"}
    if current_user.is_following(user):
        return {"message": "Already following user."}
    current_user.follow(user)
    db.session.commit()
    return {"message": "You are now following {}".format(user.username)}
