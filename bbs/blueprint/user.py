"""
# coding:utf-8
@Time    : 2020/12/16
@Author  : jiangwei
@mail    : jiangwei1@kylinos.cn
@File    : user.py
@Desc    : user
@Software: PyCharm
"""
import datetime
import os

from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from bbs.models import User, Notification, Post, Comments
from bbs.forms import EditUserForm, CropAvatarForm, ChangePasswordForm
from bbs.extensions import db, avatars
from bbs.setting import basedir
from bbs.utils import get_md5
from bbs.decorators import user_permission_required
user_bp = Blueprint('user', __name__, url_prefix='/user/')


@user_bp.route('/index/<user_id>/', methods=['GET', 'POST'])
@login_required
@user_permission_required
def index(user_id):
    form = EditUserForm()
    user = User.query.get_or_404(user_id)
    if form.validate_on_submit():
        slogan = form.slogan.data
        website = form.website.data
        location = form.location.data
        username = form.user_name.data
        nickname = form.nickname.data
        user.nickname = nickname
        user.username = username
        user.slogan = slogan
        user.website = website
        user.location = location
        db.session.commit()
        flash('资料编辑成功!', 'success')
        return redirect(url_for('.index', user_id=user_id))
    form.user_email.data = user.email
    form.user_name.data = user.username
    form.nickname.data = user.nickname
    form.website.data = user.website
    form.slogan.data = user.slogan
    form.location.data = user.location
    notices = get_notices_counts()
    return render_template('frontend/user/user-index.html', user=user, form=form, notices=notices)


def get_notices_counts():
    notices = Notification.query.filter(Notification.read == 0, Notification.receive_id == current_user.id). \
        order_by(Notification.timestamp.desc()).all()
    return notices


@user_bp.route('/notifications/<user_id>/')
@login_required
@user_permission_required
def notifications(user_id):
    user = User.query.get_or_404(user_id)
    notices = get_notices_counts()
    page = request.args.get('page', default=1, type=int)
    per_page = current_app.config['BBS_PER_PAGE']
    pagination = Notification.query.filter(Notification.receive_id == user_id, Notification.read == 1).paginate(
        page=page,
        per_page=per_page)
    read_notices = pagination.items
    return render_template('frontend/user/user-notification-read.html', user=user, notices=notices,
                           read_notices=read_notices, tag=pagination.total > per_page)


@user_bp.route('notification-unread/<user_id>/')
@login_required
def unread(user_id):
    user = User.query.get_or_404(user_id)
    notices = get_notices_counts()
    page = request.args.get('page', default=1, type=int)
    per_page = current_app.config['BBS_PER_PAGE']
    pagination = Notification.query.filter(Notification.receive_id == user_id, Notification.read == 0).paginate(
        page=page,
        per_page=per_page)
    unread_notices = pagination.items
    return render_template('frontend/user/user-notification-unread.html', user=user, notices=notices,
                           unread_notices=unread_notices, tag=pagination.total > per_page)


@user_bp.route('/contacts/<user_id>/')
@login_required
@user_permission_required
def contact(user_id):
    user = User.query.get_or_404(user_id)
    notices = get_notices_counts()
    return render_template('frontend/user/user-contact.html', user=user, notices=notices)


@user_bp.route('/user-edit/<user_id>/', methods=['GET', 'POST'])
@login_required
@user_permission_required
def edit_avatar(user_id):
    crop_form = CropAvatarForm()
    pwd_form = ChangePasswordForm()
    user = User.query.get_or_404(user_id)
    notices = get_notices_counts()
    return render_template('frontend/user/user-avatar.html', user=user, crop_form=crop_form, pwd_form=pwd_form,
                           notices=notices)


@user_bp.route('/change-password/<user_id>/', methods=['GET', 'POST'])
@login_required
@user_permission_required
def change_password(user_id):
    pwd_form = ChangePasswordForm()
    if pwd_form.validate_on_submit():
        password = pwd_form.password2.data
        current_user.set_password(password)
        db.session.commit()
        flash('密码修改成功！', 'success')
    user = User.query.get_or_404(current_user.id)
    notices = get_notices_counts()
    return render_template('frontend/user/user-password.html', pwd_form=pwd_form, user=user, notices=notices)


@user_bp.route('/user-privacy-setting/<user_id>/', methods=['GET', 'POST'])
@login_required
@user_permission_required
def privacy_setting(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        post_range = request.form.get('postPrivacy')
        comment_range = request.form.get('commentPrivacy')
        collect_range = request.form.get('collectPrivacy')
        contact_range = request.form.get('contactPrivacy')
        user.post_range_id = post_range
        user.comment_range_id = comment_range
        user.collect_range_id = collect_range
        user.contact_range_id = contact_range
        db.session.commit()
        flash('数据更新成功!', 'success')
    notices = get_notices_counts()
    return render_template('frontend/user/user-privacy-setting.html', user=user, notices=notices)


@user_bp.route('/upload-avatar/', methods=['POST'])
@login_required
def upload_avatar():
    file = request.files.get('image')
    filename = file.filename
    filename = get_md5(str(datetime.datetime.now())) + '.' + filename.split(r'.')[-1]
    upload_path = os.path.join(basedir, 'resources/avatars/raw/', filename)
    file.save(upload_path)
    current_user.avatar_raw = filename
    db.session.commit()
    return redirect(url_for('.edit_avatar', user_id=current_user.id))


@user_bp.route('/crop-avatar/', methods=['POST'])
@login_required
def crop_avatar():
    x = request.form.get('x')
    y = request.form.get('y')
    w = request.form.get('w')
    h = request.form.get('h')
    if current_user.avatar_raw:
        filename = 'raw/' + current_user.avatar_raw
    else:
        filename = None
    files = avatars.crop_avatar(filename, x, y, w, h)
    current_user.avatar = '/normal/image/avatars/' + files[2]
    db.session.commit()
    return redirect(url_for('.edit_avatar', user_id=current_user.id))


@user_bp.route('/trash-station-post/<user_id>/')
@login_required
@user_permission_required
def trash_station_post(user_id):
    page = request.args.get('page', default=1, type=int)
    per_page = current_app.config['BBS_PER_PAGE']
    pagination = Post.query.filter(Post.author_id == user_id, Post.status_id == 2).paginate(page=page,
                                                                                            per_page=per_page)
    posts = pagination.items
    user = User.query.get_or_404(user_id)
    notices = get_notices_counts()
    return render_template('frontend/user/user-trash-post.html', posts=posts, tag=pagination.total > per_page,
                           user=user, pagination=pagination, notices=notices)


@user_bp.route('/trash-station-comment/<user_id>/')
@login_required
@user_permission_required
def trash_station_comment(user_id):
    page = request.args.get('page', default=1, type=int)
    per_page = current_app.config['BBS_PER_PAGE']
    pagination = Comments.query.filter(Comments.author_id == user_id, Comments.delete_flag == 1). \
        paginate(page=page, per_page=per_page)
    comments = pagination.items
    user = User.query.get_or_404(user_id)
    notices = get_notices_counts()
    return render_template('frontend/user/user-trash-comment.html', comments=comments, pagination=pagination,
                           tag=pagination.total > per_page, user=user, notices=notices)


@user_bp.route('/post-recover/<post_id>/')
@login_required
def post_delete_or_recover(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author_id != current_user.id:
        flash('你无权操作!', 'info')
        return redirect(request.referrer)
    if post.status_id == 1:
        post.status_id = 2
    else:
        post.status_id = 1
    db.session.commit()
    flash('帖子状态操作成功!', 'success')
    return redirect(request.referrer)


@user_bp.route('/comment-operator/<comment_id>/')
@login_required
def comment_operator(comment_id):
    comment = Comments.query.get_or_404(comment_id)
    if comment.author_id != current_user.id:
        flash('你无权操作!', 'info')
        return redirect(request.referrer)
    if comment.delete_flag == 1:
        comment.delete_flag = 0
    else:
        comment.delete_flag = 1
    db.session.commit()
    flash('评论状态操作成功！', 'success')
    return redirect(request.referrer)
