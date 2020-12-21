"""
coding:utf-8
file: __init__.py
@author: jiangwei
@contact: jiangwei_1994124@163.com
@time: 2020/11/26 21:42
@desc:
"""
import logging
from logging.handlers import RotatingFileHandler

import click
from flask import Flask, render_template
from bbs.extensions import db, migrate, login_manager, bs, avatars, ck, moment
from bbs.setting import DevelopmentConfig
from bbs.models import *
from bbs.blueprint.index import index_bp
from bbs.blueprint.auth import auth_bp
from bbs.blueprint.normal import normal_bp
from bbs.blueprint.post import post_bp
from bbs.blueprint.profile import profile_bp
from bbs.blueprint.user import user_bp
from bbs.fake import generate_user, generate_post, generate_real_post
from bbs.utils import get_text_plain


def create_app(config_name=None):
    app = Flask('bbs')
    app.config.from_object(DevelopmentConfig)
    register_extensions(app)
    register_cmd(app)
    register_bp(app)
    register_error_handlers(app)
    register_log(app)
    return app


def register_extensions(app: Flask):
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bs.init_app(app)
    avatars.init_app(app)
    ck.init_app(app)
    moment.init_app(app)


def register_bp(app: Flask):
    app.register_blueprint(index_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(normal_bp)
    app.register_blueprint(post_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(user_bp)


def register_error_handlers(app: Flask):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('error/400.html'), 400

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('error/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('error/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('error/500.html'), 500


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

    @app.cli.command()
    def admin():
        click.confirm('这个操作会清空整个数据库,要继续吗?', abort=True)
        db.drop_all()
        click.echo('清空数据库完成!')
        db.create_all()
        init_status()
        click.echo('初始化状态表完成!')
        init_cate()
        click.echo('初始化帖子类别表完成!')
        init_colleges()
        click.echo('初始化学院表完成!')
        init_permission()
        click.echo('初始化权限表完成!')
        init_role()
        click.echo('初始化角色表完成!')
        Range.init_range()
        click.echo('初始化隐私表完成!')
        db.session.commit()
        click.echo('数据库初始化完成!')
        click.confirm('是否添加测试数据?', abort=True)
        generate_fake_data()


def init_status():
    s1 = Status(name='正常')
    db.session.add(s1)
    s2 = Status(name='禁用')
    db.session.add(s2)
    db.session.commit()


def init_cate():
    categories = ['杂谈', '趣事', '表白', '寻物', '咸鱼', '活动']
    for category in categories:
        pc = PostCategory(name=category)
        db.session.add(pc)
    db.session.commit()


def init_colleges():
    colleges = ['计算机科学与技术学院', '信息与通信工程学院', '法学院', '外国语学院', '体育学院', '生命科学学院', '文学院']
    for college in colleges:
        c = College(name=college)
        db.session.add(c)
    db.session.commit()


def init_permission():
    permissions = ['ALL', 'SOME', 'LITTLE']
    for per in permissions:
        p = Permission(name=per)
        db.session.add(p)
    db.session.commit()


def init_role():
    roles = ['超级管理员', '老师', '学生']
    r1 = Role(name=roles[0], permission_id=1)
    r2 = Role(name=roles[1], permission_id=2)
    r3 = Role(name=roles[2], permission_id=3)
    db.session.add(r1)
    db.session.add(r2)
    db.session.add(r3)
    db.session.commit()


def init_report_cate():
    reports_categories = ['违反法律、时政敏感',
                          '色情淫秽、血腥暴恐',
                          '未经许可的广告行为',
                          '低俗谩骂、攻击引战',
                          '造谣谩骂',
                          '其他违法版规的内容']
    for cate in reports_categories:
        rc = ReportCate(name=cate)
        db.session.add(rc)
    db.session.commit()


def generate_fake_data():
    generate_user()
    generate_post()
    generate_real_post()


def register_log(app: Flask):
    app.logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler = RotatingFileHandler('logs/bbs.log', maxBytes=10 * 1024 * 1024, backupCount=10)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    # if not app.debug:
    app.logger.addHandler(file_handler)