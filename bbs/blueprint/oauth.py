"""
# coding:utf-8
@Time    : 2022/03/08
@Author  : jiangwei
@File    : oauth.py
@Desc    : oauth
@email   : qq804022023@gmail.com
@Software: PyCharm
"""
from flask import Blueprint, abort, redirect, url_for, flash
from flask_oauthlib.client import OAuthResponse
import os
from flask_login import current_user, login_user
from bbs.models import User
from bbs.extensions import oauth, db
from functools import wraps

headers = {
    'User-Agent': ' Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
}


def check_oauth_enable(func):
    @wraps(func)
    def inner(provider_name):
        from bbs.utils import Config
        if not Config().read(['admin', 'oauth']):
            flash('管理员没有开启第三方登录功能！', 'info')
            return redirect(url_for('index_bp.index'))
        return func(provider_name)
    return inner


github = oauth.remote_app(
    name='github',
    consumer_key=os.getenv('GITHUB_CLIENT_ID'),
    consumer_secret=os.getenv('GITHUB_CLIENT_SECRET'),
    request_token_params={'scope': 'user'},
    base_url='https://api.github.com',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize'
)

gitee = oauth.remote_app(
    name='gitee',
    consumer_key=os.getenv('GITEE_CLIENT_ID'),
    consumer_secret=os.getenv('GITEE_CLIENT_SECRET'),
    request_token_params={'scope': 'user_info'},
    base_url='https://gitee.com/api/v5/user',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://gitee.com/oauth/token',
    authorize_url='https://gitee.com/oauth/authorize',
)

oschina = oauth.remote_app(
    name='oschina',
    consumer_key=os.getenv('OSCHINA_CLIENT_ID'),
    consumer_secret=os.getenv('OSCHINA_CLIENT_SECRET'),
    request_token_params={'scope': 'user_info'},
    base_url='https://www.oschina.net/action/openapi/user',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://www.oschina.net/action/openapi/token',
    authorize_url='https://www.oschina.net/action/oauth2/authorize',
    access_token_headers=headers
)

providers = {
    'github': github,
    'gitee': gitee,
    'oschina': oschina
}

profile_endpoints = {
    'github': 'user',
    'gitee': 'user',
    'oschina': 'user'
}

THIRD_PARTY = {
    'github': 1,
    'gitee': 2,
    'oschina': 3
}

oauth_bp = Blueprint('oauth_bp', __name__)


def get_social_profile(provider, token):
    profile_endpoint = profile_endpoints[provider.name]
    if provider.name == 'oschina':
        import requests
        response = requests.get('https://www.oschina.net/action/openapi/user?access_token=%s' % token, headers={'User-Agent': 'xxx'})
        response = response.json()
    else:
        response = provider.get(profile_endpoint, token=token)

    if provider.name == 'github':
        username = response.data.get('login')
        website = response.data.get('html_url')
        email = response.data.get('email')
        bio = response.data.get('bio')
        avatar = response.data.get('avatar_url')

    elif provider.name == 'gitee':
        username = response.data.get('login')
        website = response.data.get('blog')
        email = response.data.get('email')
        bio = response.data.get('bio')
        avatar = response.data.get('avatar_url')

    elif provider.name == 'oschina':
        username = response.get('name')
        website = response.get('url')
        email = response.get('email')
        bio = response.get('bio', '')
        avatar = response.get('avatar')

    return username, website, email, bio, avatar


@oauth_bp.route('/login/<provider_name>')
@check_oauth_enable
def oauth_login(provider_name):
    if provider_name not in providers.keys():
        abort(404)
    if current_user.is_authenticated:
        return redirect(url_for('blog_bp.index'))

    callback = url_for('.oauth_callback', provider_name=provider_name, _external=True)
    return providers[provider_name].authorize(callback=callback)


@oauth_bp.route('/callback/<provider_name>')
def oauth_callback(provider_name):
    try:
        if provider_name not in providers.keys():
            abort(404)
        provider = providers[provider_name]
        response = provider.authorized_response()
        if response is not None:
            if provider_name == 'github':
                access_token = response.get('access_token')
            if provider_name == 'gitee':
                access_token = response.get('access_token')
            if provider_name == 'oschina':
                access_token = response.get('access_token')
        else:
            access_token = None

        if access_token is None:
            flash('权限拒绝，请稍后再试!', 'danger')
            return redirect(url_for('auth.login'))

        username, website, email, bio, avatar = get_social_profile(provider, access_token)

        if email is None:
            flash('未能正确的获取到您的邮箱，请到第三方社交网络设置邮箱后登录！', 'danger')
            return redirect(url_for('auth.login'))

        user = User.query.filter_by(email=email).first()
        if user is None:
            user = User(username=username, email=email, website=website, avatar=avatar, nickname=username, slogan=bio,
                        account_type=THIRD_PARTY.get(provider_name), college_id=1)
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=True)
            flash('使用{}社交账号登录成功!'.format(provider.name), 'success')
            return redirect(url_for('profile.index', user_id=user.id))
        login_user(user, remember=True)
        flash('使用{}社交账号登录成功!'.format(provider.name), 'success')
        return redirect(url_for('index_bp.index'))
    except:
        import traceback
        traceback.print_exc()
        flash('使用{}登录出现了意外了~稍后再试吧~'.format(provider.name), 'danger')
        return redirect(url_for('auth.login'))
