"""
coding:utf-8
file: setting.py
@author: jiangwei
@contact: jiangwei_1994124@163.com
@time: 2020/11/26 21:46
@desc:
"""
import os

class BaseConfig(object):
    SECRET_KEY = os.getenv('SECRET_KEY')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DATABASE_USER = os.getenv('DB_USER', 'root')
    DATABASE_PWD = os.getenv('DB_PWD')

class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI ='mysql+pymysql://{}:{}@127.0.0.1/bbs?charset=utf8mb4'.format(BaseConfig.DATABASE_USER,
                                                                                            BaseConfig.DATABASE_PWD)
    REDIS_URL = "redis://localhost"
