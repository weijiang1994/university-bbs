"""
# coding:utf-8
@Time    : 2020/12/01
@Author  : jiangwei
@File    : auth.py
@Software: PyCharm
"""
import datetime
import time
from bbs.constants import PHONE_TYPE
from flask import Blueprint, render_template, flash, redirect, url_for, request, current_app
from bbs.models import User, College, VerifyCode, LoginLog
from bbs.extensions import db, rd
from bbs.forms import RegisterForm, LoginForm, ResetPasswordForm
from flask_login import current_user, login_user, logout_user
from sqlalchemy import or_
from bbs.utils import Config, generate_token, validate_token, generate_ver_code, deserialize_token, ip_recognized
from bbs.email import send_reset_password_email

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login/', methods=['GET', 'POST'])
def login():
    conf = Config()
    oauth = conf.read(['admin', 'oauth'])
    third_parties = conf.read(['admin', 'third-party'])
    if current_user.is_authenticated:
        return redirect(url_for('index_bp.index'))
    _next = request.args.get('next', url_for('index_bp.index'))
    form = LoginForm()
    if form.validate_on_submit():
        usr = form.usr_email.data
        pwd = form.password.data
        user = User.query.filter(or_(User.username == usr, User.email == usr.lower())).first()
        if user is not None:
            if user.status.name == '禁用':
                flash('该账号目前处于封禁状态，如需解禁请联系网站管理员!', 'info')
                return redirect(url_for('.login'))
            if user.check_password(pwd):
                if login_user(user, form.remember_me.data):
                    today = datetime.date.today()
                    # 通过Nginx反向代理会导致IP为127.0.0.1
                    remote_ip = request.headers.get('X-Real-Ip')
                    if remote_ip is None:
                        remote_ip = request.remote_addr
                    # 保存登录日志
                    user_agent = request.user_agent
                    existed_login_today = LoginLog.query.filter(
                        LoginLog.ip_address == remote_ip,
                        LoginLog.timestamps.ilike('%{}%'.format(today))
                    ).first()
                    # 查询IP属地
                    if remote_ip == '127.0.0.1':
                        ip_region = 'Localhost'
                    else:
                        try:
                            result = ip_recognized.recognize_region(remote_ip)
                            ip_region = '-'.join([result.get('region'), result.get('city')])
                        except Exception:
                            # 防止网络超时或未知IP导致异常
                            ip_region = 'Unknown'

                    if not existed_login_today:
                        ll = LoginLog(
                            timestamps=datetime.datetime.now(),
                            ip_address=remote_ip,
                            user_id=user.id,
                            device=user_agent.platform,
                            browser=user_agent.browser,
                            agent=user_agent.string,
                            ip_region=ip_region,
                            login_account=form.usr_email.data,
                            device_type='Phone' if user_agent.platform in PHONE_TYPE else 'Computer'
                        )
                        db.session.add(ll)
                    else:
                        existed_login_today.timestamps = datetime.datetime.now()
                        existed_login_today.device = user_agent.platform
                        existed_login_today.browser = user_agent.browser
                        existed_login_today.agent = user_agent.string
                        existed_login_today.ip_region = ip_region
                        existed_login_today.login_account = form.usr_email.data,
                        existed_login_today.device_type = 'Phone' if user_agent.platform in PHONE_TYPE else 'Computer'
                    db.session.commit()
                    flash('登录成功!', 'success')
                    return redirect(_next)
            else:
                flash('无效的密码', 'info')
        else:
            flash('无效的邮箱或用户名.', 'info')
    return render_template('frontend/auth/login.html', form=form, oauth=oauth, third_parties=third_parties)


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
        captcha = request.form.get('captcha')
        code = VerifyCode.query.filter(VerifyCode.who == email, VerifyCode.is_work == 1).order_by(
            VerifyCode.timestamps.desc()).first()
        if code:
            if code.val != int(captcha):
                flash('验证码错误!', 'danger')
                return redirect(request.referrer)
            elif code.expire_time < datetime.datetime.now():
                flash('验证码已过期!', 'danger')
                return redirect(request.referrer)
        else:
            flash('请先发送验证码到邮箱!', 'info')
            return redirect(request.referrer)

        user = User(username=username,
                    college_id=college,
                    nickname=nickname,
                    email=email,
                    password=password,
                    status_id=1)
        user.generate_avatar()
        user.set_password(password)
        code.is_work = False
        db.session.add(user)
        db.session.commit()
        flash('注册成功,欢迎加入二狗学院!', 'success')
        return redirect(url_for('.login'))
    return render_template('frontend/auth/register.html', colleges=colleges, form=form)


@auth_bp.route('/forget-password')
def forget():
    return render_template('frontend/auth/forget-password.html')


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    email = request.form.get('email')
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('邮箱不存在,请输入正确的邮箱!', 'danger')
        return redirect(url_for('.forget'))
    ver_code = generate_ver_code()
    # 将验证码设置到redis中,过期时间为10分钟
    rd.set(user.id, ver_code, ex=current_app.config['EXPIRE_TIME'])
    token = generate_token(user=user, expire_in=600)
    send_reset_password_email(user=user, token=token, ver_code=ver_code)
    flash('验证邮件发送成功，请到邮箱查看然后重置密码!', 'success')
    return render_template('frontend/auth/reset-password-continue.html')


@auth_bp.route('/reset-confirm', methods=['GET', 'POST'])
def reset_confirm():
    token = request.args.get('token', None)
    if not token:
        flash('参数不足', 'danger')
        return redirect(url_for('.login'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        data = deserialize_token(token)
        if data is None:
            flash('认证失败，无效的token！', 'danger')
            return redirect(url_for('.login'))

        if rd.get(data.get('id')) != form.captcha.data:
            flash('请输入正确的验证码', 'danger')
            return redirect(request.referrer)

        user = User.query.filter_by(id=data.get('id')).first()
        if user:
            user.set_password(form.password.data)
            db.session.commit()
            # delete cached captcha if password resetting successfully
            rd.delete(data.get('id'))
            flash('密码重置成功！', 'success')
            return redirect(url_for('.login'))
        else:
            flash('无效的token: 系统错误', 'danger')
            return redirect(url_for('.login'))
    return render_template('frontend/auth/reset-password.html',
                           form=form)
