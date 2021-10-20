"""
# coding:utf-8
@Time    : 2021/06/29
@Author  : jiangwei
@File    : post_manage.py
@Desc    : post_manage
@Software: PyCharm
"""
from flask import Blueprint, render_template, request, jsonify
from bbs.models import Post
from flask_login import current_user
from bbs.extensions import db


be_post_manage_bp = Blueprint('post_manage', __name__, url_prefix='/backend/post')


@be_post_manage_bp.route('/post-audit/', methods=['GET', 'POST'])
@be_post_manage_bp.route('/post-audit/<post_id>/', methods=['GET', 'POST'])
@admin_permission_required
def post_audit(post_id=None):
    if post_id is None:
        if request.method == 'POST':
            page = request.form.get('page', default=1, type=int)
            limit = request.form.get('limit', default=10, type=int)
            pagination = Post.query.filter_by(status_id=3).paginate(page=page, per_page=limit)
            audit_posts = pagination.items
            audit_post = render_audit_table(pagination, audit_posts)
            return jsonify(audit_post)
        return render_template('backend/post/post-audit.html', user=current_user)
    else:
        if request.method == 'POST':
            tag = request.form.get('tag')
            post = Post.query.filter_by(id=post_id).first()
            if tag:
                post.status_id = 1
            else:
                post.status_id = 4
            db.session.commit()
            return jsonify({'tag': 1, 'info': '帖子审核完成!'})

        post = Post.query.filter_by(id=post_id).first()
        return render_template('backend/post/post-audit-detail.html', user=current_user, post=post)


def render_audit_table(pagination, posts):
    audit_post = {"code": 0, "msg": "audit posts", "count": pagination.total}
    data = []
    for post in posts:
        p = {
            'id': post.id,
            'username': post.user.username,
            'post-title': post.title,
            'c-time': post.create_time
        }
        data.append(p)
    audit_post['data'] = data
    return audit_post
