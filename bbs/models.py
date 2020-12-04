"""
coding:utf-8
file: models.py
@author: jiangwei
@contact: jiangwei_1994124@163.com
@time: 2020/11/26 21:45
@desc:
"""
from werkzeug.security import generate_password_hash, check_password_hash
from flask_avatars import Identicon
from bbs.extensions import db
import datetime
from flask_login import UserMixin


class User(db.Model, UserMixin):
    __tablename__ = 't_user'

    id = db.Column(db.INTEGER, primary_key=True, nullable=False, index=True, autoincrement=True)
    username = db.Column(db.String(40), nullable=False, index=True, unique=True, comment='user name')
    nickname = db.Column(db.String(40), nullable=False, unique=True, comment='user nick name')
    password = db.Column(db.String(256), comment='user password')
    email = db.Column(db.String(128), unique=True, nullable=False, comment='user register email')
    slogan = db.Column(db.String(40), default='')
    avatar = db.Column(db.String(100), nullable=False, comment='user avatar')
    create_time = db.Column(db.DATETIME, default=datetime.datetime.now)

    status_id = db.Column(db.INTEGER, db.ForeignKey('t_status.id'))
    college_id = db.Column(db.INTEGER, db.ForeignKey('t_college.id'))
    role_id = db.Column(db.INTEGER, db.ForeignKey('t_role.id'), default=3, comment='user role id default is 3 '
                                                                                   'that is student role')

    college = db.relationship('College', back_populates='user')
    role = db.relationship('Role', back_populates='user')
    post = db.relationship('Post', back_populates='user', cascade='all')
    status = db.relationship('Status', back_populates='user')
    collect = db.relationship('Collect', back_populates='user', cascade='all')
    post_report = db.relationship('PostReport', back_populates='user', cascade='all')

    def set_password(self, pwd):
        self.password = generate_password_hash(pwd)

    def check_password(self, pwd):
        return check_password_hash(self.password, pwd)

    def generate_avatar(self):
        icon = Identicon()
        files = icon.generate(self.username)
        self.avatar = '/normal/image/avatars/' + files[2]


class College(db.Model):
    __tablename__ = 't_college'

    id = db.Column(db.INTEGER, primary_key=True, nullable=False, autoincrement=True, index=True)
    name = db.Column(db.String(100), nullable=False)
    create_time = db.Column(db.DATETIME, default=datetime.datetime.now)

    user = db.relationship('User', back_populates='college', cascade='all')


class Role(db.Model):
    __tablename__ = 't_role'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True, index=True)
    name = db.Column(db.String(40), nullable=False)
    permission_id = db.Column(db.INTEGER, db.ForeignKey('t_permission.id'), nullable=False)

    user = db.relationship('User', back_populates='role', cascade='all')
    permission = db.relationship('Permission', back_populates='role')


class Permission(db.Model):
    __tablename__ = 't_permission'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True, index=True)
    name = db.Column(db.String(40), nullable=False)

    role = db.relationship('Role', back_populates='permission', cascade='all')


class PostCategory(db.Model):
    __tablename__ = 't_postcate'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    name = db.Column(db.String(40), nullable=False)
    create_time = db.Column(db.Date, default=datetime.date.today)

    post = db.relationship('Post', back_populates='cats', cascade='all')


class Post(db.Model):
    __tablename__ = 't_post'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True, index=True)
    title = db.Column(db.String(100), index=True, nullable=False)
    content = db.Column(db.TEXT, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.datetime.now)
    is_anonymous = db.Column(db.INTEGER, default=0, comment='post is anonymous? 1: yes 0: no')
    read_times = db.Column(db.INTEGER, default=0)
    likes = db.Column(db.INTEGER, default=0, comment='like post persons')
    unlikes = db.Column(db.INTEGER, default=0, comment='unlike post persons')
    collects = db.Column(db.INTEGER, default=0, comment='collect post persons')

    cate_id = db.Column(db.INTEGER, db.ForeignKey('t_postcate.id'))
    author_id = db.Column(db.INTEGER, db.ForeignKey('t_user.id'))
    status_id = db.Column(db.INTEGER, db.ForeignKey('t_status.id'), default=1)

    cats = db.relationship('PostCategory', back_populates='post')
    user = db.relationship('User', back_populates='post')
    status = db.relationship('Status', back_populates='post')
    collect = db.relationship('Collect', back_populates='post', cascade='all')
    post_report = db.relationship('PostReport', back_populates='post', cascade='all')


class Status(db.Model):
    __tablename__ = 't_status'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True, index=True)
    name = db.Column(db.String(40), nullable=False)

    post = db.relationship('Post', back_populates='status', cascade='all')
    user = db.relationship('User', back_populates='status', cascade='all')


class Comments(db.Model):
    __tablename__ = 't_comments'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)


class Collect(db.Model):
    __tablename__ = 't_collect'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    user_id = db.Column(db.INTEGER, db.ForeignKey('t_user.id'))
    post_id = db.Column(db.INTEGER, db.ForeignKey('t_post.id'))
    timestamps = db.Column(db.DateTime, default=datetime.datetime.now)

    user = db.relationship('User', back_populates='collect')
    post = db.relationship('Post', back_populates='collect')


class PostReport(db.Model):
    __tablename__ = 't_post_report'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    post_id = db.Column(db.INTEGER, db.ForeignKey('t_post.id'))
    user_id = db.Column(db.INTEGER, db.ForeignKey('t_user.id'))
    report_cate_id = db.Column(db.INTEGER, db.ForeignKey('t_report_cate.id'))
    rep_content = db.Column(db.String(200), nullable=False, default='')
    flag = db.Column(db.INTEGER, default=0, comment='is it new info flag')
    timestamps = db.Column(db.DateTime, default=datetime.datetime.now)

    post = db.relationship('Post', back_populates='post_report')
    user = db.relationship('User', back_populates='post_report')
    report_cate = db.relationship('ReportCate', back_populates='post_report')


class ReportCate(db.Model):
    __tablename__ = 't_report_cate'

    id = db.Column(db.INTEGER, primary_key=True, nullable=False, autoincrement=True)
    name = db.Column(db.String(40), nullable=False)
    timestamps = db.Column(db.DateTime, default=datetime.datetime.now)

    post_report = db.relationship('PostReport', back_populates='report_cate', cascade='all')

