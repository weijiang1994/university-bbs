"""
# coding:utf-8
@Time    : 2021/01/04
@Author  : jiangwei
@mail    : jiangwei1@kylinos.cn
@File    : user_manage.py
@Desc    : user_manage
@Software: PyCharm
"""
from flask import Blueprint, request, render_template, jsonify
from flask_login import login_required, current_user
from bbs.decorators import admin_permission_required
from bbs.models import User

be_user_manage_bp = Blueprint('user_manage', __name__, url_prefix='/backend/user')


@be_user_manage_bp.route('/website-user/', methods=['GET', 'POST'])
@login_required
@admin_permission_required
def website_user():
    if request.method == 'POST':
        print(request.args)
        page = request.form.get('page', default=1, type=int)
        limit = request.form.get('limit', default=10, type=int)
        print('page is ', page)
        print('limit is ', limit)
        pagination = User.query.paginate(page=page, per_page=limit)
        users = pagination.items
        user_dict = {"code": 0, "msg": "website users", "count": pagination.total}
        data = []
        for user in users:
            s = {'id': user.id,
                 'username': user.username,
                 'nickname': user.nickname,
                 'city': user.location,
                 'slogan': user.slogan,
                 'website': user.website}
            data.append(s)
        user_dict['data'] = data
        return jsonify(user_dict)
    return render_template('backend/user/website-user.html', user=current_user)


@be_user_manage_bp.route('/admin-user/', methods=['GET', 'POST'])
@login_required
@admin_permission_required
def admin_user():

    return render_template('backend/user/admin-user.html', user=current_user)
