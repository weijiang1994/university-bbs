"""
# coding:utf-8
@Time    : 2021/01/04
@Author  : jiangwei
@mail    : jiangwei1@kylinos.cn
@File    : index.py
@Desc    : index
@Software: PyCharm
"""
from flask import Blueprint, render_template
from bbs.decorators import admin_permission_required
from flask_login import login_required, current_user


be_index_bp = Blueprint('be_index', __name__, url_prefix='/backend')


@be_index_bp.route('/index/')
@login_required
@admin_permission_required
def index():
    return render_template('backend/index.html', user=current_user)
