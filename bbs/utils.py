"""
# coding:utf-8
@Time    : 2020/12/02
@Author  : jiangwei
@mail    : jiangwei1@kylinos.cn
@File    : utils.py
@Software: PyCharm
"""
import re
from bbs.models import User, Post
from faker import Faker
from bbs.extensions import db
import random

try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin

from flask import request, url_for, redirect


def validate_username(username):
    r = re.match('^[a-zA-Z0-9_]*$', username)
    return True if r else False


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def redirect_back(default='index_bp.index', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))


def generate_user():
    fa = Faker()
    for i in range(50):
        user = User(username=fa.name().strip(), email=fa.email(), nickname=fa.name(), status_id=1)
        user.set_password('12345678')
        user.generate_avatar()
        db.session.add(user)
    db.session.commit()


def generate_post():
    fa = Faker()
    for i in range(56):
        content = ''
        for text in fa.texts():
            content += text
        p = Post(title=fa.sentence(), cate_id=1, is_anonymous=1, content=content, author_id=random.randint(1, 50))
        db.session.add(p)
    db.session.commit()
