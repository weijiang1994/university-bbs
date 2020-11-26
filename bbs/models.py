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

    colleges = db.relationship('College', back_populates='User')

class College(db.Model):
    __tablename__ = 't_college'

    id = db.Column(db.INTEGER, primary_key=True, nullable=False, autoincrement=True, index=True)
    name = db.Column(db.String(100), nullable=False)
    create_time = db.Column(db.DATETIME, default=datetime.datetime.now)


class Role(db.Model):
    __tablename__ = 't_role'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True, index=True)
    