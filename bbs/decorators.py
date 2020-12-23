"""
# coding:utf-8
@Time    : 2020/12/15
@Author  : jiangwei
@mail    : jiangwei1@kylinos.cn
@File    : decorators.py
@Desc    : decorators
@Software: PyCharm
"""
from functools import wraps
from flask import abort, flash

from flask_login import current_user


def admin_permission_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.role_id == 1:
            abort(403)
        return func(*args, **kwargs)

    return decorated_function


def user_permission_required(func):
    @wraps(func)
    def authorized(user_id):
        if current_user.id != int(user_id):
            flash('这是别人的东西，你无权干涉!', 'danger')
            abort(403)
        return func(user_id)
    return authorized
