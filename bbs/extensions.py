"""
coding:utf-8
file: extensions.py
@author: jiangwei
@time: 2020/11/26 21:45
@desc:
"""
import os

from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_avatars import Avatars
from flask_ckeditor import CKEditor
import redis
from flask_moment import Moment
from flask_mail import Mail
from flask_whooshee import Whooshee
from flask_apscheduler import APScheduler
from flask_oauthlib.client import OAuth

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
bs = Bootstrap()
avatars = Avatars()
ck = CKEditor()
pool = redis.ConnectionPool(
    host=os.getenv('REDIS_HOST', 'localhost'), 
    port=os.getenv('REDIS_PORT', 6379), 
    decode_responses=True
)
rd = redis.Redis(connection_pool=pool)
moment = Moment()
mail = Mail()
whooshee = Whooshee()
aps = APScheduler()
oauth = OAuth()


@login_manager.user_loader
def load_user(user_id):
    from bbs.models import User
    user = User.query.filter_by(id=user_id).first()
    return user


login_manager.login_view = 'auth.login'
login_manager.login_message = u'请先登陆!'
login_manager.login_message_category = 'info'
