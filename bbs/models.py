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
    username = db.Column(db.String(40), nullable=False, index=True, comment='user name')
    password = db.Column(db.String(256), comment='user password')
    slogan = db.Column(db.String(40), default='')
    create_time = db.Column(db.DATETIME, default=datetime.datetime.now)
    college_id = db.Column(db.INTEGER, db.ForeignKey('t_college.id'))
    role_id = db.Column(db.INTEGER, db.ForeignKey('t_role.id'))

    college = db.relationship('College', back_populates='user')
    role = db.relationship('Role', back_populates='user')


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
