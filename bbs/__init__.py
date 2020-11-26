"""
coding:utf-8
file: __init__.py
@author: jiangwei
@contact: jiangwei_1994124@163.com
@time: 2020/11/26 21:42
@desc:
"""
from flask import Flask
from bbs.extensions import db
from bbs.setting import DevelopmentConfig


def create_app(config_name=None):
    app = Flask('bbs')
    app.config.from_object(DevelopmentConfig)
    register_extensions(app)

    return app


def register_extensions(app:Flask):
    db.init_app(app)