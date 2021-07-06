"""
coding:utf-8
file: index.py
@author: jiangwei
@contact: jiangwei_1994124@163.com
@time: 2020/11/26 23:04
@desc:
"""
from flask import Blueprint, render_template, request, current_app, jsonify
from bbs.models import Post, VisitStatistic, Notification
from bbs.extensions import db, gcard
from sqlalchemy.sql.expression import func
from bbs.decorators import statistic_traffic
import requests
from flask_login import current_user


index_bp = Blueprint('index_bp', __name__)


@index_bp.route('/')
@index_bp.route('/index/')
@statistic_traffic(db, VisitStatistic)
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(status_id=1).order_by(Post.update_time.desc()). \
        paginate(page, per_page=current_app.config['BBS_PER_PAGE'])
    latest = pagination.items
    tag = pagination.total > current_app.config['BBS_PER_PAGE']
    return render_template('frontend/index/index.html',
                           latest=latest,
                           pagination=pagination,
                           tag=tag,
                           unread_count=get_notification_count())


def get_notification_count():
    if current_user.is_authenticated:
        unread_count = Notification.query.filter_by(receive_id=current_user.id, read=0).count()
    else:
        unread_count = 0
    return unread_count


@index_bp.route('/hot-post/')
@statistic_traffic(db, VisitStatistic)
def hot():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.read_times.desc()).paginate(page, per_page=current_app.config['BBS_PER_PAGE'])
    hots = pagination.items
    tag = pagination.total > current_app.config['BBS_PER_PAGE']
    return render_template('frontend/index/hot-post.html',
                           hots=hots,
                           pagination=pagination,
                           tag=tag,
                           unread_count=get_notification_count())


@index_bp.route('/rand-post/')
@statistic_traffic(db, VisitStatistic)
def rands():
    rand = Post.query.filter_by(status_id=1).order_by(func.random()).limit(20)
    return render_template('frontend/index/rand-post.html', rands=rand, unread_count=get_notification_count())


@index_bp.route('/load-one/')
def load_one():
    res = requests.post('https://2dogz.cn/load-one/')
    return jsonify({'one': res.json().get('one')})


@index_bp.route('/load-github/')
def load_github():
    theme = request.cookies.get('theme', 'darkly')
    return jsonify(gcard.create(theme=theme).get_raw_data())
