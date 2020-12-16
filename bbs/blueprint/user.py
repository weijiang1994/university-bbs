"""
# coding:utf-8
@Time    : 2020/12/16
@Author  : jiangwei
@mail    : jiangwei1@kylinos.cn
@File    : user.py
@Desc    : user
@Software: PyCharm
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from bbs.models import User
user_bp = Blueprint('user', __name__, url_prefix='/user/')


@user_bp.route('/index/<user_id>/')
@login_required
def index(user_id):
    judge(user_id)
    user = User.query.get_or_404(user_id)
    return render_template('frontend/user/user-index.html', user=user)


def judge(user_id):
    if current_user.id != int(user_id):
        flash('您没有权限访问该页面!', 'danger')
        return redirect(url_for('index_bp.index'))


@user_bp.route('/notifications/<user_id>/')
@login_required
def notifications(user_id):
    judge(user_id)
    user = User.query.get_or_404(user_id)
    return render_template('frontend/user/user-notification.html', user=user)


@user_bp.route('/contacts/<user_id>/')
@login_required
def contact(user_id):
    judge(user_id)
    user = User.query.get_or_404(user_id)
    return render_template('frontend/user/user-contact.html', user=user)
