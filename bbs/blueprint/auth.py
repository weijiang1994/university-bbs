"""
# coding:utf-8
@Time    : 2020/12/01
@Author  : jiangwei
@mail    : jiangwei1@kylinos.cn
@File    : auth.py
@Software: PyCharm
"""
from datetime import datetime

from flask import Blueprint, render_template, request, flash, redirect, url_for
from bbs.models import User, College
from bbs.extensions import db
from bbs.forms import RegisterForm, LoginForm
from flask_login import current_user, login_user, logout_user
from sqlalchemy import or_

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index_bp.index'))
    form = LoginForm()
    if form.validate_on_submit():
        usr = form.usr_email.data
        pwd = form.password.data
        user = User.query.filter(or_(User.username == usr, User.email == usr.lower())).first()
        if user is not None and user.status.name == '禁用':
            flash('您的账号处于封禁状态,禁止登陆！联系管理员解除封禁!', 'danger')
            return redirect(url_for('.login'))

        if user is not None and user.check_password(pwd):
            if login_user(user, form.remember_me.data):
                flash('登录成功!', 'success')
                return redirect(url_for('index_bp.index'))
        elif user is None:
            flash('无效的邮箱或用户名.', 'danger')
        else:
            flash('无效的密码', 'danger')
    return render_template('frontend/login.html', form=form)


@auth_bp.route('/logout/', methods=['GET'])
def logout():
    logout_user()
    flash('退出成功!', 'success')
    return redirect(url_for('index_bp.index'))


# noinspection PyArgumentList
@auth_bp.route('/register/', methods=['GET', 'POST'])
def register():
    colleges = College.query.all()
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.user_name.data
        nickname = form.nickname.data
        password = form.confirm_pwd.data
        email = form.user_email.data
        college = form.colleges.data
        user = User(username=username, college_id=college, nickname=nickname, email=email, password=password,
                    status_id=1, post_range_id=1, comment_range_id=1, collect_range_id=1, contact_range_id=1)
        user.generate_avatar()
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('注册成功,欢迎加入二狗学院!', 'success')
        return redirect(url_for('.login'))
    return render_template('frontend/register.html', colleges=colleges, form=form)
