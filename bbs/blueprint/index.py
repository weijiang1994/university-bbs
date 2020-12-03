"""
coding:utf-8
file: index.py
@author: jiangwei
@contact: jiangwei_1994124@163.com
@time: 2020/11/26 23:04
@desc:
"""
from flask import Blueprint, render_template, request
from bbs.models import Post
from sqlalchemy.sql.expression import func
index_bp = Blueprint('index_bp', __name__)


@index_bp.route('/')
@index_bp.route('/index/')
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(status_id=1).order_by(Post.update_time.desc()).paginate(page, per_page=10)
    latest = pagination.items
    hots = Post.query.order_by(Post.read_times.desc()).all()[:20]
    rands = Post.query.filter_by(status_id=1).order_by(func.random()).limit(20)
    return render_template('frontend/index.html', hots=hots, rands=rands, latest=latest, pagination=pagination)

