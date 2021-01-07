"""
# coding:utf-8
@Time    : 2021/01/04
@Author  : jiangwei
@mail    : jiangwei1@kylinos.cn
@File    : index.py
@Desc    : index
@Software: PyCharm
"""
from flask import Blueprint, render_template, jsonify
from bbs.decorators import admin_permission_required
from flask_login import login_required, current_user
from bbs.models import User, Comments, Post, AdminLog
from bbs.utils import hardware_monitor

be_index_bp = Blueprint('be_index', __name__, url_prefix='/backend')


@be_index_bp.route('/index/')
@login_required
@admin_permission_required
def index():
    users = User.query.all()
    posts = Post.query.all()
    comments = Comments.query.all()
    admin_logs = AdminLog.query.order_by(AdminLog.timestamps.desc())[:10]
    return render_template('backend/index.html', user=current_user, users=len(users), posts=len(posts),
                           comments=len(comments), admin_logs=admin_logs)


@be_index_bp.route('/init-data/', methods=['GET', 'POST'])
@login_required
@admin_permission_required
def init_data():
    cpu_per, me_per = hardware_monitor()
    return jsonify({'tag': 1, 'cpu_per': cpu_per, 'me_per': me_per})

