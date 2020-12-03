"""
coding:utf-8
file: setting.py
@author: jiangwei
@contact: jiangwei_1994124@163.com
@time: 2020/11/26 21:46
@desc:
"""
import os

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class BaseConfig(object):
    SECRET_KEY = os.getenv('SECRET_KEY')

    BBS_THEMES = {'Darkly': 'darkly', 'Sketchy': 'sketchy', 'Journal': 'journal', 'Flatly': 'flatly',
                  'Cerulean': 'cerulean', 'Cyborg': 'cyborg', 'Lumen': 'lumen', 'Minty': 'minty'}

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DATABASE_USER = os.getenv('DATABASE_USER')
    DATABASE_PWD = os.getenv('DATABASE_PWD')
    DATABASE_HOST = os.getenv('DATABASE_HOST')
    DATABASE_PORT = os.getenv('DATABASE_PORT')

    BBS_UPLOAD_PATH = os.path.join(basedir, 'resources')
    AVATARS_SAVE_PATH = BBS_UPLOAD_PATH + '/avatars/'

    # CKEditor configure
    CKEDITOR_SERVE_LOCAL = True
    CKEDITOR_ENABLE_CODESNIPPET = True
    CKEDITOR_HEIGHT = 400
    CKEDITOR_FILE_UPLOADER = 'normal.image_upload'


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}/bbs?charset=utf8mb4'.format(BaseConfig.DATABASE_USER,
                                                                                    BaseConfig.DATABASE_PWD,
                                                                                    BaseConfig.DATABASE_HOST)
    REDIS_URL = "redis://localhost"
