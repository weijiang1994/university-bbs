"""
# coding:utf-8
@Time    : 2020/12/01
@Author  : jiangwei
@mail    : jiangwei1@kylinos.cn
@File    : auth.py
@Software: PyCharm
"""
from flask import Blueprint, render_template


auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login/', methods=['GET', 'POST'])
def login():
    return render_template('frontend/login.html')


@auth_bp.route('/register/', methods=['GET', 'POST'])
def register():
    return render_template('frontend/register.html')