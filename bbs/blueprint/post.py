"""
# coding:utf-8
@Time    : 2020/12/02
@Author  : jiangwei
@mail    : jiangwei1@kylinos.cn
@File    : post.py
@Software: PyCharm
"""
from flask import Blueprint, render_template

post_bp = Blueprint('post', __name__, url_prefix='/post')


@post_bp.route('/new/', methods=['GET', 'POST'])
def new_post():
    return render_template('frontend/new_post.html')
