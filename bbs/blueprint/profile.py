"""
# coding:utf-8
@Time    : 2020/12/09
@Author  : jiangwei
@mail    : jiangwei1@kylinos.cn
@File    : profile.py
@Software: PyCharm
"""
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from bbs.models import User, Comments, Post

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')


@profile_bp.route('/user/<user_id>/')
@profile_bp.route('/posts/<user_id>/')
def index(user_id):
    print(user_id)
    user = User.query.get_or_404(user_id)
    pagination = Post.query.filter(Post.author_id == user_id, Post.status_id == 1).order_by(
        Post.create_time.desc()).paginate()
    posts = pagination.items
    return render_template('frontend/profile.html', user=user, pagination=pagination, posts=posts)


@profile_bp.route('/comment/<user_id>/')
def profile_comment(user_id):
    page = request.args.get('page', default=1, type=int)
    user = User.query.get_or_404(user_id)
    pagination = Comments.query.filter(Comments.author_id == user.id, Comments.delete_flag == 0).order_by(
        Comments.timestamps.desc()).paginate(page=page, per_page=20)
    comments = pagination.items
    return render_template('frontend/profile-comment.html', user=user, comments=comments)
