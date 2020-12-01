"""
coding:utf-8
file: models.py
@author: jiangwei
@contact: jiangwei_1994124@163.com
@time: 2020/11/26 21:45
@desc:
"""
from bbs.extensions import db
import datetime


class User(db.Model):
    __tablename__ = 't_user'

    id = db.Column(db.INTEGER, primary_key=True, nullable=False, index=True, autoincrement=True)
    username = db.Column(db.String(40), nullable=False, index=True, unique=True, comment='user name')
    password = db.Column(db.String(256), comment='user password')
    email = db.Column(db.String(128), unique=True, nullable=False, comment='user register email')
    slogan = db.Column(db.String(40), default='')
    create_time = db.Column(db.DATETIME, default=datetime.datetime.now)
    college_id = db.Column(db.INTEGER, db.ForeignKey('t_college.id'))
    role_id = db.Column(db.INTEGER, db.ForeignKey('t_role.id'))

    college = db.relationship('College', back_populates='user')
    role = db.relationship('Role', back_populates='user')
    post = db.relationship('Post', back_populates='user', cascade='all')


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

    post = db.relationship('Post', back_populates='cats', cascade='all')


class Post(db.Model):
    __tablename__ = 't_post'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True, index=True)
    title = db.Column(db.String(100), index=True, nullable=False)
    content = db.Column(db.TEXT, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.datetime.now)
    cate_id = db.Column(db.INTEGER, db.ForeignKey('t_postcate.id'))
    author_id = db.Column(db.INTEGER, db.ForeignKey('t_user.id'))
    is_anonymous = db.Column(db.INTEGER, default=0, comment='post is anonymous? 1: yes 0: no')
    read_times = db.Column(db.INTEGER, default=0)
    status_id = db.Column(db.INTEGER, db.ForeignKey('t_status.id'))

    cats = db.relationship('PostCategory', back_populates='post')
    user = db.relationship('User', back_populates='post')
    status = db.relationship('Status', back_populates='post')


class Status(db.Model):
    __tablename__ = 't_status'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True, index=True)
    name = db.Column(db.String(40), nullable=False)

    post = db.relationship('Post', back_populates='status', cascade='all')


class Comments(db.Model):

    __tablename__ = 't_comments'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
