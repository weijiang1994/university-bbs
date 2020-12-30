"""
# coding:utf-8
@Time    : 2020/12/04
@Author  : jiangwei
@mail    : jiangwei1@kylinos.cn
@File    : fake.py
@Software: PyCharm
"""
import os
import random

from faker import Faker
from bbs.models import User, Post
from bbs.extensions import db
from bbs.setting import basedir
from bbs.utils import get_text_plain


# noinspection PyArgumentList
def generate_user():
    fa = Faker()
    for i in range(30):
        user = User(username=fa.name().replace(' ', '').lower(),
                    college_id=random.randint(1, 7),
                    email=fa.email(),
                    nickname=fa.name(),
                    status_id=1,
                    comment_range_id=1,
                    collect_range_id=1,
                    post_range_id=1,
                    contact_range_id=1)
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
        p = Post(title=fa.sentence(),
                 cate_id=random.randint(1, 6),
                 is_anonymous=random.randint(1, 2),
                 content=content,
                 textplain=get_text_plain(content),
                 author_id=random.randint(1, 30))
        db.session.add(p)
    db.session.commit()


def generate_real_post():
    for root, dirs, files in os.walk(basedir + '/test-post/'):
        for file in files:
            with open(root + file, 'r') as f:
                content = f.read()
            p = Post(title=file,
                     cate_id=1,
                     is_anonymous=1,
                     content=content,
                     textplain=get_text_plain(content),
                     author_id=random.randint(1, 50))
            db.session.add(p)
    db.session.commit()
