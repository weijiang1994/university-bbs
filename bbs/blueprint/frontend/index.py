"""
coding:utf-8
file: index.py
@author: jiangwei
@time: 2020/11/26 23:04
@desc:
"""
from flask import Blueprint, render_template, request, current_app, jsonify
from bbs.models import Post, VisitStatistic, Notification, Comments, UserInterest, PostCategory
from bbs.extensions import db
import random
from sqlalchemy.sql.expression import func, not_, or_
from bbs.decorators import statistic_traffic
import requests
from flask_login import current_user
import datetime

index_bp = Blueprint('index_bp', __name__)


def get_index_category():
    if current_user.is_authenticated:
        user_interests = UserInterest.query.with_entities(UserInterest.cate_id).filter(
            UserInterest.user_id == current_user.id). \
            order_by(UserInterest.visit_times.desc()).limit(5).all()

        if len(user_interests) < 5:
            user_interests = [user_interest[0] for user_interest in user_interests]
            categories = PostCategory.query.filter(PostCategory.id.in_(user_interests)).all()

            pcs = PostCategory.query. \
                filter(not_(PostCategory.id.in_(user_interests))). \
                order_by(func.random()). \
                limit(5 - len(user_interests)).all()
            categories += pcs
    else:
        categories = PostCategory.query.order_by(func.random()).limit(5)
    return categories


@index_bp.route('/')
@index_bp.route('/index/')
@statistic_traffic(db, VisitStatistic)
def index():
    # 只获取过去30天以内的帖子
    day = datetime.datetime.today() - datetime.timedelta(days=30)
    posts = []

    if current_user.is_authenticated:
        # 查找用户收藏的帖子类型
        user_interests = UserInterest.query.with_entities(UserInterest.cate_id).filter(
            UserInterest.user_id == current_user.id). \
            order_by(UserInterest.visit_times.desc()).limit(5).all()

        # 根据用户兴趣获取推荐的帖子
        if user_interests:
            user_interests = [user_interest[0] for user_interest in user_interests]

            posts += Post.query.filter(Post.cate_id.in_(user_interests),
                                       Post.status_id == 1,
                                       Post.create_time > day).order_by(Post.update_time.desc()).all()

            post_ids = [post.id for post in posts]

            if len(posts) >= 20:
                posts = random.sample(posts, 20)
            else:
                posts += Post.query. \
                    filter(not_(Post.id.in_(post_ids)),
                           Post.status_id == 1). \
                    order_by(Post.update_time.desc(), func.random()). \
                    limit(20 - len(posts))
        else:
            posts += Post.query.filter(Post.status_id == 1).order_by(Post.update_time.desc(), func.random()).limit(20)

        # 如果用户没有收藏帖子，则随机推荐五个类别
        if 0 < len(user_interests) < 5:
            categories = PostCategory.query.filter(PostCategory.id.in_(user_interests)).all()
            categories += PostCategory.query.filter(not_(PostCategory.id.in_(user_interests))).order_by(
                func.random()).limit(5 - len(user_interests))

        elif len(user_interests) == 0:
            categories = PostCategory.query.order_by(func.random()).limit(5)

        elif len(user_interests) >= 5:
            categories = PostCategory.query.filter(PostCategory.id.in_(user_interests)).all()
    else:
        posts += Post.query.filter(Post.status_id == 1).order_by(Post.update_time.desc(), func.random()).limit(20)
        categories = PostCategory.query.order_by(func.random()).limit(5)

    hot_posts = get_td_hot_posts()
    rand_posts = get_random_posts()
    return render_template('frontend/index/index.html',
                           posts=posts,
                           categories=categories,
                           unread_count=get_notification_count(),
                           hot_posts=hot_posts,
                           rand_posts=rand_posts)


def get_notification_count():
    if current_user.is_authenticated:
        unread_count = Notification.query.filter_by(receive_id=current_user.id, read=0).count()
    else:
        unread_count = 0
    return unread_count


@index_bp.route('/latest')
@statistic_traffic(db, VisitStatistic)
def latest():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query. \
        filter_by(status_id=1). \
        order_by(Post.update_time.desc()). \
        paginate(page, per_page=current_app.config['BBS_PER_PAGE'])
    posts = pagination.items
    tag = pagination.total > current_app.config['BBS_PER_PAGE']
    categories = get_index_category()
    rand_posts = get_random_posts()
    return render_template('frontend/index/latest.html',
                           posts=posts,
                           tag=tag,
                           pagination=pagination,
                           categories=categories,
                           rand_posts=rand_posts)


@index_bp.route('/hot-post/')
@statistic_traffic(db, VisitStatistic)
def hot():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query. \
        filter_by(status_id=1). \
        order_by(Post.read_times.desc()). \
        paginate(page, per_page=current_app.config['BBS_PER_PAGE'])

    hots = pagination.items
    tag = pagination.total > current_app.config['BBS_PER_PAGE']
    categories = get_index_category()
    rand_posts = get_random_posts()
    return render_template('frontend/index/hot-post.html',
                           hots=hots,
                           pagination=pagination,
                           tag=tag,
                           unread_count=get_notification_count(),
                           categories=categories,
                           rand_posts=rand_posts)


def get_random_posts():
    day = datetime.date.today() - datetime.timedelta(days=30)
    rand = Post.query.filter(Post.status_id == 1,
                             Post.create_time > day).order_by(func.random(), Post.update_time.desc()).limit(5).all()
    if len(rand) < 5:
        rand += Post.query.filter(Post.status_id == 1).order_by(func.random(), Post.update_time.desc()).limit(5 - len(rand)).all()
    return rand


def get_td_hot_posts():
    import datetime
    td = datetime.date.today()
    td_coms = Comments.query.with_entities(Comments.post_id, func.count(Comments.post_id)). \
        filter(Comments.timestamps.contains(str(td))). \
        group_by(Comments.post_id). \
        order_by((func.count(Comments.post_id)).desc()).limit(6)
    hot_posts = []
    for td in td_coms:
        p = Post.query.filter(Post.id == td[0], Post.status_id == 1).first()
        hot_posts.append(p)
    return hot_posts


@index_bp.route('/load-one/')
def load_one():
    res = requests.post('https://2dogz.cn/load-one/')
    return jsonify({'one': res.json().get('one')})


@index_bp.route('/load-github/')
def load_github():
    theme = request.cookies.get('bbs_themes', 'darkly')
    if theme in ['darkly', 'cyborg', 'slate', 'superhero']:
        theme = 'darkly'
    ret = get_ghinfo(theme=theme)
    if not ret:
        return jsonify({'tag': 0, 'info': 'Get shield failed!'})
    return jsonify({'tag': 1, 'star': ret[0], 'fork': ret[1]})


def get_ghinfo(theme='default'):
    import requests
    stars = 'https://img.shields.io/github/stars/weijiang1994/university-bbs?style=social'
    forks = 'https://img.shields.io/github/forks/weijiang1994/university-bbs?style=social'
    if theme == 'darkly':
        stars = 'https://img.shields.io/github/stars/weijiang1994/university-bbs?style=flat-square'
        forks = 'https://img.shields.io/github/forks/weijiang1994/university-bbs?style=flat-square'
    try:
        star = requests.get(stars).text
        fork = requests.get(forks).text
        return star, fork
    except Exception as e:
        return False
