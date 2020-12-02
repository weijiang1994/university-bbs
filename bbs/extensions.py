"""
coding:utf-8
file: extensions.py
@author: jiangwei
@contact: jiangwei_1994124@163.com
@time: 2020/11/26 21:45
@desc:
"""
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_avatars import Avatars

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
bs = Bootstrap()
avatars = Avatars()


@login_manager.user_loader
def load_user(user_id):
    from bbs.models import User
    user = User.query.filter_by(id=user_id).first()
    return user


login_manager.login_view = 'auth_bp.login'
login_manager.login_message = u'请先登陆!'
login_manager.login_message_category = 'danger'
