"""
coding:utf-8
file: __init__.py
@author: jiangwei
@time: 2020/11/26 21:42
@desc:
"""
import logging
from logging.handlers import RotatingFileHandler

import click
from flask import Flask, render_template
from bbs.extensions import db, migrate, login_manager, bs, avatars, ck, moment, mail, whooshee, aps, oauth
from bbs.setting import DevelopmentConfig, ProductionConfig, BaseConfig
from bbs.models import *
from bbs.blueprint.frontend.index import index_bp
from bbs.blueprint.frontend.auth import auth_bp
from bbs.blueprint.frontend.normal import normal_bp
from bbs.blueprint.frontend.post import post_bp
from bbs.blueprint.frontend.profile import profile_bp
from bbs.blueprint.frontend.user import user_bp
from bbs.blueprint.frontend.oauth import oauth_bp
from bbs.fake import generate_user, generate_post, generate_real_post, generate_post_tag
from bbs.utils import get_text_plain, get_backend_url
import os
from bbs.setting import basedir
from bbs import task


def create_app(config_name=None):
    app = Flask('bbs')
    if config_name is None:
        app.config.from_object(DevelopmentConfig)
    else:
        app.config.from_object(ProductionConfig)
    app.jinja_env.filters['empty'] = translate_empty
    app.jinja_env.filters['my_truncate'] = my_truncate
    register_extensions(app)
    register_cmd(app)
    register_bp(app)
    register_error_handlers(app)
    register_log(app)
    app.context_processor(get_backend_url)
    return app


def register_extensions(app: Flask):
    db.init_app(app)
    db.app = app
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bs.init_app(app)
    avatars.init_app(app)
    ck.init_app(app)
    moment.init_app(app)
    mail.init_app(app)
    whooshee.init_app(app)
    scheduler_init(app)
    oauth.init_app(app)


def register_bp(app: Flask):
    app.register_blueprint(index_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(normal_bp)
    app.register_blueprint(post_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(oauth_bp)


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
    def addvisit():
        from bbs.models import VisitStatistic, CommentStatistic, PostStatistic, SearchStatistic
        start_date = datetime.datetime.strptime('2021-12-01', '%Y-%m-%d')
        import random
        while start_date < datetime.datetime.today():
            start_date += datetime.timedelta(days=1)
            vs = VisitStatistic(day=start_date, times=0)
            cs = CommentStatistic(day=start_date, times=0)
            ps = PostStatistic(day=start_date, times=0)
            ss = SearchStatistic(day=start_date, times=0)
            db.session.add(vs)
            db.session.add(cs)
            db.session.add(ps)
            db.session.add(ss)
        db.session.commit()

    @app.cli.command()
    def init():
        click.confirm('这个操作会清空整个数据库,要继续吗?', abort=True)
        db.drop_all()
        click.echo('清空数据库完成!')
        db.create_all()
        generate_post_tag()
        click.echo('初始化帖子标签表完成!')
        init_status()
        click.echo('初始化状态表完成!')
        init_cate()
        click.echo('初始化帖子类别表完成!')
        init_colleges()
        click.echo('初始化学院表完成!')
        init_user_permission()
        click.echo('初始化角色表完成!')
        init_user_permission()
        click.echo('初始化权限表完成!')
        init_role_permission_ship()
        click.echo('初始化角色权限关系表完成!')
        init_permission()
        click.echo('初始化权限表完成!')
        init_role()
        click.echo('初始化角色表完成!')
        Range.init_range()
        click.echo('初始化隐私表完成!')
        Gender.init_gender()
        click.echo('初始化性别表成功!')
        OperatorCate.init_cate()
        click.echo('初始化操作类别表成功!')
        init_report_cate()
        click.echo('初始化举报类别表成功!')
        db.session.commit()
        click.echo('数据库初始化完成!')

        click.confirm('是否添加测试数据?', abort=True)
        create_folders()
        generate_fake_data()

    @app.cli.command()
    def superuser():
        import re
        reg = '^[a-zA-Z0-9_]*$'
        inp = True
        while inp:
            username = input('请输入超级管理员用户名(不能为中文):')
            nickname = input('请输入超级管理员昵称:')
            pwd = input('请输入超级管理员密码(大于8位):')
            if re.match(reg, username) or len(pwd) > 8:
                inp = False

        u = User(username=username, nickname=nickname, role_id=1, email='admin@2dogzbbs.cn', status_id=1, college_id=1)
        u.set_password(pwd=pwd)
        u.generate_avatar()
        db.session.add(u)
        db.session.commit()
        click.echo('超级管理员添加成功!')


def create_folders():
    if not os.path.exists(os.path.join(basedir, 'resources')):
        os.mkdir(os.path.join(basedir, 'resources'))
    for path in ['avatars', 'comments', 'posts']:
        if not os.path.exists(os.path.join(basedir, 'resources', path)):
            os.mkdir(os.path.join(basedir, 'resources', path))


def init_status():
    status = ['正常', '禁用', '未审核', '审核失败']
    for s in status:
        s1 = Status(name=s)
        db.session.add(s1)
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


def init_user_role():
    roles = ['sys-admin', 'post-auditor', 'teacher', 'student']
    for role in roles:
        db.session.add(UserRole(role=role))


def init_user_permission():
    permissions = ['sys-admin', 'post-audit', 'post-block', 'comment-block', 'normal']
    for permission in permissions:
        db.session.add(UserPermission(permission=permission))


def init_role_permission_ship():
    roles = UserRole.query.all()
    audit_pid = UserPermission.query.filter_by(permission='post-audit').first().id
    post_block_pid = UserPermission.query.filter_by(permission='post-block').first().id
    comment_block_pid = UserPermission.query.filter_by(permission='comment-block').first().id
    normal_pid = UserPermission.query.filter_by(permission='normal').first().id
    for role in roles:
        if role.role == 'sys-admin':
            for permission in UserPermission.query.all():
                db.session.add(RolePermissionShip(rid=role.id, pid=permission))
        elif role.role == 'post-auditor':
            db.session.add(RolePermissionShip(rid=role.id, pid=audit_pid))
            db.session.add(RolePermissionShip(rid=role.id, pid=post_block_pid))
            db.session.add(RolePermissionShip(rid=role.id, pid=comment_block_pid))
            db.session.add(RolePermissionShip(rid=role.id, pid=normal_pid))
        elif role.role == 'teacher':
            db.session.add(RolePermissionShip(rid=role.id, pid=post_block_pid))
            db.session.add(RolePermissionShip(rid=role.id, pid=comment_block_pid))
            db.session.add(RolePermissionShip(rid=role.id, pid=normal_pid))
        else:
            db.session.add(RolePermissionShip(rid=role.id, pid=normal_pid))


def init_report_cate():
    reports_categories = ['违反法律、时政敏感',
                          '色情淫秽、血腥暴恐',
                          '未经许可的广告行为',
                          '低俗谩骂、攻击引战',
                          '造谣毁谤',
                          '其他违法版规的内容']
    for cate in reports_categories:
        rc = ReportCate(name=cate)
        db.session.add(rc)
    db.session.commit()


def generate_fake_data():
    generate_user()
    generate_post()


def register_log(app: Flask):
    app.logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    if not os.path.exists('logs'):
        os.makedirs('logs')
    file_handler = RotatingFileHandler('logs/bbs.log', maxBytes=10 * 1024 * 1024, backupCount=10)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    # if not app.debug:
    app.logger.addHandler(file_handler)


def translate_empty(msg):
    if msg is None or msg == '':
        return '暂无描述信息'
    return msg


def my_truncate(msg, length=10):
    if len(msg) > length:
        return msg[:length] + '...'
    return msg


def scheduler_init(app):
    """
    保证系统只启动一次定时任务
    :param app: 当前flask实例
    :return: None
    """
    import atexit
    import platform
    if platform.system() != 'Windows':
        fcntl = __import__("fcntl")
        f = open(basedir + '/resources/scheduler.lock', 'wb')
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            aps.init_app(app)
            aps.start()
        except:
            pass

        def unlock():
            fcntl.flock(f, fcntl.LOCK_UN)
            f.close()

        atexit.register(unlock)
    else:
        msvcrt = __import__('msvcrt')

        if not os.path.exists(os.path.join(basedir, 'resources')):
            os.mkdir(os.path.join(basedir, 'resources'))

        f = open(basedir + '/resources/scheduler.lock', 'wb')
        try:
            msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
            aps.init_app(app)
            aps.start()
        except:
            pass

        def _unlock_file():
            try:
                f.seek(0)
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
            except:
                pass

        atexit.register(_unlock_file)
