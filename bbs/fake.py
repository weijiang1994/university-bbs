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
from bbs.models import User, Post, Tag, PostTagShip
from bbs.extensions import db
from bbs.setting import basedir
from bbs.utils import get_text_plain

fa = Faker(locale='zh-CN')


def generate_post_tag():
    for i in range(1, 31):
        db.session.add(Tag(name=fa.word()))
    db.session.commit()


def generate_user():
    for i in range(30):
        user = User(username=fa.user_name().strip().lower() + str(random.randint(1, 9)),
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
        db.session.flush()
        for j in range(random.randint(1, 4)):
            tag_id = random.randint(1, 30)
            db.session.add(PostTagShip(post_id=p.id, tag_id=tag_id))
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
