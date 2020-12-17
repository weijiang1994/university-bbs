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

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from bbs.models import User
from bbs.forms import EditUserForm, UploadAvatarForm, CropAvatarForm, ChangePasswordForm
from bbs.extensions import db, avatars
from bbs.setting import basedir
from bbs.utils import get_md5

user_bp = Blueprint('user', __name__, url_prefix='/user/')


@user_bp.route('/index/<user_id>/', methods=['GET', 'POST'])
@login_required
def index(user_id):
    form = EditUserForm()
    judge(user_id)
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
    return render_template('frontend/user/user-index.html', user=user, form=form)


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


@user_bp.route('/user-edit/<user_id>/')
@login_required
def edit_user(user_id):
    upload_form = UploadAvatarForm()
    crop_form = CropAvatarForm()
    pwd_form = ChangePasswordForm()
    judge(user_id)
    user = User.query.get_or_404(user_id)
    return render_template('frontend/user/user-edit.html', user=user, upload_form=upload_form, crop_form=crop_form,
                           pwd_form=pwd_form)


@user_bp.route('/user-privacy-setting/<user_id>/')
@login_required
def privacy_setting(user_id):
    judge(user_id)
    user = User.query.get_or_404(user_id)
    return render_template('frontend/user/user-privacy-setting.html', user=user)


@user_bp.route('/upload-avatar/', methods=['POST'])
@login_required
def upload_avatar():
    file = request.files.get('image')
    filename = file.filename
    filename = get_md5(str(datetime.datetime.now())) + '.' + filename.split(r'.')[-1]
    upload_path = os.path.join(basedir, 'resources/avatar_raw', filename)
    file.save(upload_path)
    current_user.avatar_raw = filename
    db.session.commit()
    return redirect(url_for('.edit_user', user_id=current_user.id))
