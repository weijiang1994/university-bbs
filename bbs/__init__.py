"""
coding:utf-8
file: __init__.py
@author: jiangwei
@contact: jiangwei_1994124@163.com
@time: 2020/11/26 21:42
@desc:
"""
import click
from flask import Flask
from bbs.extensions import db, migrate, login_manager, bs, avatars, ck
from bbs.setting import DevelopmentConfig
from bbs.models import *
from bbs.blueprint.index import index_bp
from bbs.blueprint.auth import auth_bp
from bbs.blueprint.normal import normal_bp
from bbs.blueprint.post import post_bp


def create_app(config_name=None):
    app = Flask('bbs')
    app.config.from_object(DevelopmentConfig)
    register_extensions(app)
    register_cmd(app)
    register_bp(app)
    return app


def register_extensions(app: Flask):
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bs.init_app(app)
    avatars.init_app(app)
    ck.init_app(app)


def register_bp(app: Flask):
    app.register_blueprint(index_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(normal_bp)
    app.register_blueprint(post_bp)


def register_cmd(app: Flask):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Drop database and create a new database')
    def initdb(drop):
        if drop:
            click.confirm('This operation will delete the database, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Drop tables.')
        db.create_all()
        click.echo('Initialized database.')
