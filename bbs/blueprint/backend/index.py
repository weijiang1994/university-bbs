"""
# coding:utf-8
@Time    : 2021/01/04
@Author  : jiangwei
@mail    : jiangwei1@kylinos.cn
@File    : index.py
@Desc    : index
@Software: PyCharm
"""
from flask import Blueprint, render_template, jsonify
from bbs.decorators import admin_permission_required
from flask_login import login_required, current_user
from bbs.models import User, Comments, Post, AdminLog, VisitStatistic, CommentStatistic, SearchStatistic
from bbs.utils import hardware_monitor
import datetime

be_index_bp = Blueprint('be_index', __name__, url_prefix='/backend')


@be_index_bp.route('/index/')
@login_required
@admin_permission_required
def index():
    users = User.query.all()
    posts = Post.query.all()
    comments = Comments.query.all()
    admin_logs = AdminLog.query.order_by(AdminLog.timestamps.desc())[:10]
    return render_template('backend/index.html', user=current_user, users=len(users), posts=len(posts),
                           comments=len(comments), admin_logs=admin_logs)


@be_index_bp.route('/init-data/', methods=['GET', 'POST'])
@login_required
@admin_permission_required
def init_data():
    cpu_per, me_per = hardware_monitor()
    td = datetime.date.today()
    sd = td + datetime.timedelta(days=-7)
    vsts = VisitStatistic.query.filter(VisitStatistic.day > sd).order_by(VisitStatistic.day.asc()).all()
    csts = CommentStatistic.query.filter(CommentStatistic.day > sd).order_by(CommentStatistic.day.asc()).all()
    ssts = SearchStatistic.query.filter(SearchStatistic.day > sd).order_by(SearchStatistic.day.asc()).all()
    vs = [v.times for v in vsts]
    cs = [c.times for c in csts]
    ss = [s.times for s in ssts]
    days = [str(v.day) for v in vsts]
    return jsonify({'tag': 1, 'cpu_per': cpu_per, 'me_per': me_per, 'statistics': {'days': days,
                                                                                   'vsts': vs,
                                                                                   'csts': cs,
                                                                                   'ssts': ss}})


@be_index_bp.route('/get-monitor/', methods=['GET', 'POST'])
@login_required
@admin_permission_required
def get_monitor():
    cpu_per, me_per = hardware_monitor()
    return jsonify({'tag': 1, 'cpu_per': cpu_per, 'me_per': me_per})
