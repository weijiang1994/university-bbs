"""
# coding:utf-8
@Time    : 2020/12/09
@Author  : jiangwei
@File    : profile.py
@Software: PyCharm
"""
import datetime

from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify
from flask_login import current_user, login_required

from bbs.models import User, Comments, Post, Collect, BlockUser
from bbs.blueprint.frontend.post import post_collect
from bbs.utils import TIME_RANGE, PANGU_DATE

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')


@profile_bp.route('/user/<user_id>/')
@login_required
def index(user_id):
    page = request.args.get('page', default=1, type=int)
    user = User.query.get_or_404(user_id)
    per_page = current_app.config['BBS_PER_PAGE']
    # 其他人查看用户信息时候屏蔽用户匿名发表的帖子
    if current_user.id == int(user_id):
        pagination = Post.query.filter(Post.author_id == user_id, Post.status_id == 1).order_by(
            Post.create_time.desc()).paginate(page=page, per_page=per_page)
        posts = pagination.items
    else:
        pagination, posts = get_range_post(user.id,
                                           page=page,
                                           per_page=per_page,
                                           range_day=TIME_RANGE.get(user.range_post.name))
    blocked = BlockUser.query.filter(BlockUser.user_id == current_user.id,
                                     BlockUser.block_user_id == user_id).all()
    return render_template('frontend/profile/profile.html', user=user, tag=pagination.total > per_page,
                           pagination=pagination, posts=posts, blocked=blocked)


@profile_bp.route('/comment/<user_id>/')
@login_required
def profile_comment(user_id):
    page = request.args.get('page', default=1, type=int)
    user = User.query.get_or_404(user_id)
    per_page = current_app.config['BBS_PER_PAGE']
    if current_user.id == user.id:
        pagination = Comments.query.filter(Comments.author_id == user.id, Comments.delete_flag == 0).order_by(
            Comments.timestamps.desc()).paginate(page=page, per_page=per_page)
        comments = pagination.items
    else:
        pagination, comments = get_range_comment(user_id=user_id, page=page, per_page=per_page, range_day=TIME_RANGE.
                                                 get(user.range_comment.name))
    blocked = BlockUser.query.filter(BlockUser.user_id == current_user.id,
                                     BlockUser.block_user_id == user_id).all()
    return render_template('frontend/profile/profile-comment.html', tag=pagination.total > per_page, user=user,
                           pagination=pagination, comments=comments, blocked=blocked)


@profile_bp.route('/follow/<user_id>/', methods=['GET', 'POST'])
@login_required
def follow_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('我关注我自己?禁止套娃!', 'info')
        return redirect(request.referrer)
    if current_user.is_following(user):
        flash('你已经关注TA了!', 'info')
        return redirect(request.referrer)
    current_user.follow(user)
    flash('关注成功!', 'success')
    return redirect(request.referrer)


@profile_bp.route('/unfollow/<user_id>/', methods=['GET', 'POST'])
@login_required
def unfollow_user(user_id):
    user = User.query.get_or_404(user_id)
    if current_user.is_following(user):
        current_user.unfollow(user)
    if request.method == 'POST':
        return jsonify({'tag': 1})
    flash('取关成功!', 'success')
    return redirect(request.referrer)


@profile_bp.route('/collect/<user_id>/')
@login_required
def collect(user_id):
    user = User.query.get_or_404(user_id)
    page = request.args.get('page', default=1, type=int)
    per_page = current_app.config['BBS_PER_PAGE']
    if current_user.id == user.id:
        pagination = Collect.query.with_parent(user).order_by(
            Collect.timestamps.desc()).paginate(page=page, per_page=per_page)
        collects = pagination.items
    else:
        pagination, collects = get_range_collect(user, page, per_page,
                                                 range_day=TIME_RANGE.get(user.range_collect.name))
    blocked = BlockUser.query.filter(BlockUser.user_id == current_user.id,
                                     BlockUser.block_user_id == user_id).all()
    return render_template('frontend/profile/profile-collections.html', user=user, tag=pagination.total > per_page,
                           pagination=pagination, collects=collects, blocked=blocked)


@profile_bp.route('/uncollect/<post_id>')
@login_required
def uncollect(post_id):
    post_collect(post_id)
    return redirect(url_for('.collect', user_id=current_user.id))


@profile_bp.route('/social/<user_id>/')
@login_required
def follower(user_id):
    user = User.query.get_or_404(user_id)
    page = request.args.get('page', default=1, type=int)
    per_page = current_app.config['BBS_PER_PAGE_SOCIAL']
    pagination = user.followers.paginate(page, per_page)
    followers = pagination.items
    blocked = BlockUser.query.filter(BlockUser.user_id == current_user.id,
                                     BlockUser.block_user_id == user_id).all()
    return render_template('frontend/profile/profile-followers.html', tag=pagination.total > per_page, user=user,
                           pagination=pagination, followers=followers, blocked=blocked)


@profile_bp.route('/following/<user_id>/')
@login_required
def following(user_id):
    user = User.query.get_or_404(user_id)
    page = request.args.get('page', default=1, type=int)
    per_page = current_app.config['BBS_PER_PAGE_SOCIAL']
    pagination = user.following.paginate(page, per_page)
    followings = pagination.items
    blocked = BlockUser.query.filter(BlockUser.user_id == current_user.id,
                                     BlockUser.block_user_id == user_id).all()
    return render_template('frontend/profile/profile-following.html', tag=pagination.total > per_page,
                           user=user, pagination=pagination, followings=followings, blocked=blocked)


def get_range_post(user_id, page=1, per_page=10, range_day=-1):
    date = get_date(range_day)
    pagination = Post.query.filter(Post.author_id == user_id, Post.status_id == 1, Post.is_anonymous == 1,
                                   Post.create_time >= date).order_by(Post.create_time.desc()).paginate(page=page,
                                                                                                        per_page=
                                                                                                        per_page)
    posts = pagination.items
    return pagination, posts


def get_range_comment(user_id, page=1, per_page=10, range_day=-1):
    date = get_date(range_day)
    pagination = Comments.query.filter(Comments.author_id == user_id, Comments.delete_flag == 0,
                                       Comments.timestamps >= date).order_by(
        Comments.timestamps.desc()).paginate(page=page, per_page=per_page)
    comments = pagination.items
    return pagination, comments


def get_range_collect(user, page=1, per_page=10, range_day=-1):
    date = get_date(range_day)
    pagination = Collect.query.filter(Collect.timestamps > date).with_parent(user).order_by(
        Collect.timestamps.desc()).paginate(page=page,
                                            per_page=per_page)
    collects = pagination.items
    return pagination, collects


def get_date(range_day):
    if range_day == 1:
        date = datetime.datetime.strptime(PANGU_DATE, '%Y-%m-%d').date()
    else:
        date = datetime.date.today() - datetime.timedelta(range_day)
    return date
