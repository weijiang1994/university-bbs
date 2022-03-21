"""
coding:utf-8
file: setting.py
@author: jiangwei
@time: 2020/11/26 21:46
@desc:
"""
import os
from dotenv import load_dotenv
import sys

WIN = sys.platform.startswith('win')
if WIN:
    sqlite_pre = 'sqlite:///'
else:
    sqlite_pre = 'sqlite:////'

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
# 手动加载env文件,防止部署到服务器时不主动加载env获取不到服务器启动的关键参数
load_dotenv('.env')


class BaseConfig(object):
    SECRET_KEY = os.getenv('SECRET_KEY')

    BBS_THEMES = {'Darkly': 'darkly',
                  'Materia': 'materia',
                  'Sketchy': 'sketchy',
                  'Journal': 'journal',
                  'Flatly': 'flatly',
                  'Cerulean': 'cerulean',
                  'Cyborg': 'cyborg',
                  'Lumen': 'lumen',
                  'Minty': 'minty',
                  'Yeti': 'yeti',
                  'Slate': 'slate',
                  'Superhero': 'superhero',
                  'Cosmo': 'cosmo',
                  'Litera': 'litera',
                  'Lux': 'lux',
                  'Pulse': 'pulse',
                  'Sandstone': 'sandstone',
                  'Simplex': 'simplex',
                  'Solar': 'solar',
                  'Spacelab': 'spacelab',
                  'United': 'united'}

    BBS_PER_PAGE = 20
    BBS_PER_PAGE_SOCIAL = 40
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # database config
    DATABASE_USER = os.getenv('DATABASE_USER')
    DATABASE_PWD = os.getenv('DATABASE_PWD')
    DATABASE_HOST = os.getenv('DATABASE_HOST')
    DATABASE_PORT = os.getenv('DATABASE_PORT')

    # mail config
    BBS_MAIL_SUBJECT_PRE = '[狗子学院]'
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = ('BBS Admin', MAIL_USERNAME)

    # celery config
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

    BBS_UPLOAD_PATH = os.path.join(basedir, 'resources')
    AVATARS_SAVE_PATH = BBS_UPLOAD_PATH + '/avatars/'

    # CKEditor configure
    CKEDITOR_SERVE_LOCAL = True
    CKEDITOR_ENABLE_CODESNIPPET = True
    CKEDITOR_HEIGHT = 400
    CKEDITOR_CODE_THEME = 'docco'
    CKEDITOR_FILE_UPLOADER = 'normal.image_upload'
    CKEDITOR_PKG_TYPE = 'full'
    # whooshee config
    WHOOSHEE_MIN_STRING_LEN = 1

    GITHUB_USERNAME = 'weijiang1994'
    GITHUB_REPO = 'university-bbs'

    SCHEDULER_API_ENABLED = True

    # Redis Configure
    EXPIRE_TIME = 60 * 10


class DevelopmentConfig(BaseConfig):
    if BaseConfig.DATABASE_USER is not None:
        SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}/bbs?charset=utf8mb4'.format(BaseConfig.DATABASE_USER,
                                                                                        BaseConfig.DATABASE_PWD,
                                                                                        BaseConfig.DATABASE_HOST)
    else:
        SQLALCHEMY_DATABASE_URI = sqlite_pre + os.path.join(basedir, 'data.db')
    REDIS_URL = "redis://localhost:6379"


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}/bbs?charset=utf8mb4'.format(BaseConfig.DATABASE_USER,
                                                                                    BaseConfig.DATABASE_PWD,
                                                                                    BaseConfig.DATABASE_HOST)
    REDIS_URL = "redis://localhost:6379"
