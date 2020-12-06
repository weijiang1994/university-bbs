"""
coding:utf-8
file: wsgi.py
@author: jiangwei
@contact: jiangwei_1994124@163.com
@time: 2020/12/6 12:18
@desc:
"""
from bbs import create_app

app = create_app(config_name='production')
