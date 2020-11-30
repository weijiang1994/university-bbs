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

    DATABASE_USER = os.getenv('DATABASE_USER')
    DATABASE_PWD = os.getenv('DATABASE_PWD')
    DATABASE_HOST = os.getenv('DATABASE_HOST')
    DATABASE_PORT = os.getenv('DATABASE_PORT')


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}/bbs?charset=utf8mb4'.format(BaseConfig.DATABASE_USER,
                                                                                    BaseConfig.DATABASE_PWD,
                                                                                    BaseConfig.DATABASE_HOST)
    REDIS_URL = "redis://localhost"
