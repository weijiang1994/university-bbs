"""
# coding:utf-8
@Time    : 2020/12/15
@Author  : jiangwei
@File    : decorators.py
@Desc    : decorators
@Software: PyCharm
"""
from functools import wraps
from flask import abort, flash, request, redirect, url_for
from flask_login import current_user
import datetime
from bbs.models import PostStatistic, Post, UserInterest
from bbs.extensions import db


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


def post_can_read(func):
    @wraps(func)
    def decorator(post_id, *args, **kwargs):
        po = Post.query.get_or_404(post_id)
        if po.status.name == '未审核':
            if current_user.is_authenticated and current_user.id == po.user.id:
                flash('该帖子正在审核中,目前只有你能查看!', 'warning')
            else:
                flash('该帖子正在审核中,暂时不能查看!', 'warning')
                return redirect(url_for('index_bp.index'))
        if po.status.name == '禁用':
            flash('该帖子处于封禁状态,暂时不能查看!', 'warning')
            return redirect(url_for('index_bp.index'))
        if po.status.name == '审核失败':
            flash('该帖子审核未通过,不能查看!', 'warning')
            return redirect(url_for('index_bp.index'))
        return func(post_id, *args, **kwargs)

    return decorator


def record_read(func):
    @wraps(func)
    def wrapper(post_id, *args, **kwargs):
        if current_user.is_authenticated:
            pt = Post.query.filter_by(id=post_id).first()
            if UserInterest.exist_user_cate(current_user.id, pt.cate_id):
                uit = UserInterest.exist_user_cate(current_user.id, pt.cate_id)
                uit.visit_times += 1
                db.session.commit()
        return func(post_id, *args, **kwargs)

    return wrapper


def log_traceback(logger):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                import traceback
                logger.error(str(traceback.format_exc()))
        return wrapper
    return decorator
