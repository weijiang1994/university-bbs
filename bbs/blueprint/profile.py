"""
# coding:utf-8
@Time    : 2020/12/09
@Author  : jiangwei
@mail    : jiangwei1@kylinos.cn
@File    : profile.py
@Software: PyCharm
"""
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from bbs.models import User
profile_bp = Blueprint('profile', __name__, url_prefix='/profile')


@profile_bp.route('/user/<user_id>/')
def index(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('frontend/profile.html', user=user)
