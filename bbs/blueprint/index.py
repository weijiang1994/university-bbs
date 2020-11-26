"""
coding:utf-8
file: index.py
@author: jiangwei
@contact: jiangwei_1994124@163.com
@time: 2020/11/26 23:04
@desc:
"""
from flask import Blueprint, render_template

index_bp = Blueprint('index_bp', __name__)


@index_bp.route('/')
@index_bp.route('/index/')
def index():
    return render_template('frontend/base.html')

