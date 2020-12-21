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


@user_bp.route('/user-edit/<user_id>/', methods=['GET', 'POST'])
@login_required
def edit_avatar(user_id):
    crop_form = CropAvatarForm()
    pwd_form = ChangePasswordForm()
    judge(user_id)
    user = User.query.get_or_404(user_id)
    return render_template('frontend/user/user-avatar.html', user=user, crop_form=crop_form, pwd_form=pwd_form)


@user_bp.route('/change-password/', methods=['GET', 'POST'])
@login_required
def change_password():
    pwd_form = ChangePasswordForm()
    judge(current_user.id)
    if pwd_form.validate_on_submit():
        password = pwd_form.password2.data
        current_user.set_password(password)
        db.session.commit()
        flash('密码修改成功！', 'success')
    user = User.query.get_or_404(current_user.id)
    return render_template('frontend/user/user-password.html', pwd_form=pwd_form, user=user)


@user_bp.route('/user-privacy-setting/<user_id>/', methods=['GET', 'POST'])
@login_required
def privacy_setting(user_id):
    judge(user_id)
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
    return render_template('frontend/user/user-privacy-setting.html', user=user)


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
    print('x is ', x)
    print('y is ', y)
    print('w is ', w)
    print('h is ', h)
    filename = 'raw/' + current_user.avatar_raw
    files = avatars.crop_avatar(filename, x, y, w, h)
    current_user.avatar = '/normal/image/avatars/'+files[2]
    db.session.commit()
    return redirect(url_for('.edit_avatar', user_id=current_user.id))
