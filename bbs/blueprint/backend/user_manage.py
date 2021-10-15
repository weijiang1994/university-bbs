"""
# coding:utf-8
@Time    : 2021/01/04
@Author  : jiangwei
@File    : user_manage.py
@Desc    : user_manage
@Software: PyCharm
"""
from flask import Blueprint, request, render_template, jsonify
from flask_login import login_required, current_user
from bbs.decorators import admin_permission_required
from bbs.models import User, AdminLog, OperatorCate, Role
from bbs.extensions import db
import json

be_user_manage_bp = Blueprint('user_manage', __name__, url_prefix='/backend/user')


@be_user_manage_bp.route('/website-user/', methods=['GET', 'POST'])
@login_required
@admin_permission_required
def website_user():
    if request.method == 'POST':
        page = request.form.get('page', default=1, type=int)
        limit = request.form.get('limit', default=10, type=int)
        keyword = request.form.get('keyword')
        cate = request.form.get('cate')
        if cate and keyword:
            if cate == 'id':
                pagination = User.query.filter_by(id=keyword).paginate(page=page, per_page=limit)
            elif cate == 'username':
                pagination = User.query.filter_by(username=keyword).paginate(page=page, per_page=limit)
            elif cate == 'email':
                pagination = User.query.filter_by(email=keyword).paginate(page=page, per_page=limit)
            else:
                pagination = User.query.filter_by(nickname=keyword).paginate(page=page, per_page=limit)
            users = pagination.items
        else:
            pagination = User.query.paginate(page=page, per_page=limit)
            users = pagination.items

        user_dict = table_render(pagination, users)
        return jsonify(user_dict)
    return render_template('backend/user/website-user.html', user=current_user)


def table_render(pagination, users):
    user_dict = {"code": 0, "msg": "website users", "count": pagination.total}
    data = []
    for user in users:
        s = {'id': user.id,
             'username': user.username,
             'nickname': user.nickname,
             'city': user.location,
             'slogan': user.slogan,
             'website': user.website,
             'join': str(user.create_time),
             'role': user.role.name,
             'email': user.email,
             'status': user.status_id,
             'gender': user.gender.name,
             'college': user.college.name}
        data.append(s)
    user_dict['data'] = data
    return user_dict


@be_user_manage_bp.route('/add-user/', methods=['GET', 'POST'])
@login_required
@admin_permission_required
def add_user():
    if request.method == 'POST':
        username = request.form.get('username')
        nickname = request.form.get('nickname')
        email = request.form.get('email')
        tag = 0
        if User.query.filter_by(username=username).first():
            info = '用户名已存在'
        elif User.query.filter_by(nickname=nickname).first():
            info = '昵称已存在'
        elif User.query.filter_by(email=email).first():
            info = '邮箱已经被注册'
        else:
            password = request.form.get('password')
            gender = request.form.get('gender')
            role = request.form.get('role')
            college = request.form.get('college')
            user = User(username=username,
                        nickname=nickname,
                        email=email,
                        gender_id=gender,
                        role_id=role,
                        status_id=1,
                        college_id=college)
            user.generate_avatar()
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            r = Role.query.filter_by(id=role).first()
            log = AdminLog(admin_id=current_user.id,
                           target_id=user.id,
                           op_id=4,
                           notes='添加了用户{},角色为{}'.format(user.username, r.name))
            db.session.add(log)
            db.session.commit()
            tag = 1
            info = '添加用户成功!'
        return jsonify({'tag': tag, 'info': info})
    return render_template('backend/user/add-user.html')


@be_user_manage_bp.route('/add-admin/', methods=['GET', 'POST'])
@login_required
@admin_permission_required
def add_admin():
    return render_template('backend/user/add-admin.html')


@be_user_manage_bp.route('/lock-or-unlock/', methods=['post'])
@login_required
@admin_permission_required
def lock_or_unlock():
    user_id = request.form.get('userId')
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({'tag': 1, 'info': '查无此人!'})
    if user.status_id == 1:
        user.status_id = 2
        al = AdminLog(admin_id=current_user.id, target_id=user.id, notes='锁定了用户{}'.format(user.username))
        db.session.add(al)
    else:
        user.status_id = 1
        al = AdminLog(admin_id=current_user.id, target_id=user.id, notes='解锁了用户{}'.format(user.username))
        db.session.add(al)
    db.session.commit()
    return jsonify({'tag': 1, 'info': '操作成功!'})


@be_user_manage_bp.route('/multi-lock-unlock/', methods=['POST'])
@login_required
@admin_permission_required
def multi_lock_unlock():
    ids = json.loads(request.get_data(as_text=True))
    users = []
    lock_count = 0
    unlock_count = 0
    for _id in ids:
        user = User.query.filter_by(id=_id).first()
        users.append(user)
    for user in users:
        if user.status_id == 1:
            user.status_id = 2
            lock_count += 1
        else:
            user.status_id = 1
            unlock_count += 1
    db.session.commit()
    return jsonify({'tag': 1, 'info': '操作成功!锁定了{}个账号,解锁了{}个账号!'.format(lock_count, unlock_count)})


@be_user_manage_bp.route('/reset-pwd/', methods=['POST'])
@login_required
@admin_permission_required
def reset_user_pwd():
    user_id = request.form.get('id')
    user = User.query.filter_by(id=user_id).first()
    user.set_password('12345678')
    db.session.commit()
    return jsonify({'tag': 1, 'info': '密码重置成功!'})


@be_user_manage_bp.route('/admin-user/', methods=['GET', 'POST'])
@login_required
@admin_permission_required
def admin_user():
    if request.method == 'POST':
        page = request.form.get('page', default=1, type=int)
        limit = request.form.get('limit', default=10, type=int)
        pagination = User.query.filter_by(role_id=1).paginate(page, limit)
        users = pagination.items
        user_dict = table_render(pagination, users)
        return jsonify(user_dict)
    return render_template('backend/user/admin-user.html', user=current_user)
