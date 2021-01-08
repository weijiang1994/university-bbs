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
from flask import abort, flash, request
from flask_login import current_user
import datetime
from bbs.models import PostStatistic


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


def statistic_traffic(database, obj):
    """
    统计网站流量装饰器
    :param database: Sqlachemy对象
    :param obj: 数据库表模型
    :return:
    """
    def decorator(func):
        # noinspection PyCallingNonCallable
        @wraps(func)
        def statistic(*args, **kwargs):
            td = datetime.date.today()
            vst = obj.query.filter_by(day=td).first()
            if isinstance(obj, PostStatistic) and request.method == 'GET':
                return func(*args, **kwargs)
            if vst is None:
                new_vst = obj(day=td, times=1)
                database.session.add(new_vst)
            else:
                vst.times += 1
            database.session.commit()
            return func(*args, **kwargs)
        return statistic
    return decorator
