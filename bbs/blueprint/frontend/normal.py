"""
# coding:utf-8
@Time    : 2020/12/02
@Author  : jiangwei
@mail    : jiangwei1@kylinos.cn
@File    : normal.py
@Software: PyCharm
"""
import datetime
import os

from bleach import clean, linkify
from flask import Blueprint, send_from_directory, request, jsonify, flash
from markdown import markdown
from bbs.setting import basedir
from flask import current_app, make_response, abort, render_template
from bbs.utils import redirect_back, MyMDStyleExtension, EMOJI_INFOS, get_md5, generate_ver_code
from flask_login import login_required
import re
from bbs.email import send_email
from bbs.models import VerifyCode, Gender, Role, College, User, Post
from bbs.extensions import db

normal_bp = Blueprint('normal', __name__, url_prefix='/normal')


@normal_bp.route('/search/')
def search():
    keyword = request.args.get('keyword')
    cate = request.args.get('category', default='user')
    page = request.args.get('page', default=1, type=int)
    if keyword.strip() == '':
        flash('搜索关键字都没有,这他妈绝对是来捣乱的!', 'info')
        return redirect_back(request.referrer)
    if cate == 'user':
        paginates = User.query.whooshee_search(keyword).paginate(per_page=20, page=page)
        items = paginates.items
    else:
        paginates = Post.query.whooshee_search(keyword).paginate(per_page=20, page=page)
        items = paginates.items
    return render_template('frontend/search-result.html', keyword=keyword, cate=cate, items=items,
                           tag=paginates.total > 20, paginates=paginates)


@normal_bp.route('/image/<string:path>/<string:filename>/', methods=['GET'])
def get_image(path, filename):
    path = basedir + '/resources/{}/'.format(path)
    return send_from_directory(path, filename)


@normal_bp.route('/image/<string:filename>/', methods=['GET'])
def get_avatar_raw(filename):
    path = basedir + '/resources/avatars/raw/'
    return send_from_directory(path, filename)


@normal_bp.route('/themes/<string:theme_name>')
def change_theme(theme_name):
    if theme_name not in current_app.config['BBS_THEMES'].keys():
        abort(404)

    response = make_response(redirect_back())
    response.set_cookie('bbs_themes', current_app.config['BBS_THEMES'].get(theme_name), max_age=30 * 24 * 60 * 60)
    return response


@normal_bp.route('/image/upload/')
def image_upload():
    pass


@normal_bp.route('/ajax-upload/', methods=['POST'])
@login_required
def ajax_upload():
    f = request.files['file']
    origin_filename = f.filename
    filename = get_md5(str(datetime.datetime.now())) + '.' + origin_filename.split(r'.')[-1]
    upload_path = os.path.join(basedir, 'resources/comments', filename)
    f.save(upload_path)
    md_str = '![{}](/normal/image/comments/{}/)'.format(origin_filename, filename)
    return jsonify({'tag': 1, 'imgPath': md_str})


@normal_bp.route('/comment/render-md/', methods=['POST'])
@login_required
def render_md():
    md = request.form.get('md')
    html = to_html(md)
    return jsonify({'html': html})


@normal_bp.route('/send-email/', methods=['POST'])
def send():
    to_email = request.form.get('user_email')
    username = request.form.get('user_name')
    ver_code = generate_ver_code()
    send_email(to_mail=to_email, subject='Captcha', template='email/verifyCode', username=username,
               ver_code=ver_code)

    # 判断是否已经存在一个最新的可用的验证码,以确保生效的验证码是用户收到最新邮件中的验证码
    exist_code = VerifyCode.query.filter(VerifyCode.who == to_email, VerifyCode.is_work == 1).order_by(
        VerifyCode.timestamps.desc()).first()
    if exist_code:
        exist_code.is_work = False
    nt = datetime.datetime.now()
    et = nt + datetime.timedelta(minutes=10)
    verify_code = VerifyCode(val=ver_code, who=to_email, expire_time=et)
    db.session.add(verify_code)
    db.session.commit()
    return jsonify({'tag': 1, 'info': '邮件发送成功!'})


# noinspection PyTypeChecker
def to_html(raw):
    allowed_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', 'abbr', 'b', 'br', 'blockquote', 'code', 'del', 'div',
                    'em', 'img', 'p', 'pre', 'strong', 'span', 'ul', 'li', 'ol']
    allowed_attributes = ['src', 'title', 'alt', 'href', 'class']
    html = markdown(raw, output_format='html',
                    extensions=['markdown.extensions.fenced_code',
                                'markdown.extensions.codehilite',
                                'markdown.extensions.tables', MyMDStyleExtension()])
    clean_html = clean(html, tags=allowed_tags, attributes=allowed_attributes)
    img_url = '<img class="img-emoji" src="/static/emojis/{}" title="{}" alt="{}">'
    for i in EMOJI_INFOS:
        for ii in i:
            emoji_url = img_url.format(ii[0], ii[1], ii[1])
            clean_html = re.sub(':{}:'.format(ii[1]), emoji_url, clean_html)
    return linkify(clean_html)


@normal_bp.route('/init-select/', methods=['GET', 'POST'])
def init_select():
    genders = Gender.query.all()
    roles = Role.query.all()
    colleges = College.query.all()
    data_dict = dict()
    g = []
    r = []
    c = []
    for gender in genders:
        g.append({'id': gender.id, 'name': gender.name})
    for role in roles:
        r.append({'id': role.id, 'name': role.name})
    for college in colleges:
        c.append({'id': college.id, 'name': college.name})
    data_dict['gender'] = g
    data_dict['role'] = r
    data_dict['college'] = c
    return jsonify({'tag': 1, 'data': data_dict})
