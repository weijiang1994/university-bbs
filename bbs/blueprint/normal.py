"""
# coding:utf-8
@Time    : 2020/12/02
@Author  : jiangwei
@mail    : jiangwei1@kylinos.cn
@File    : normal.py
@Software: PyCharm
"""
from flask import Blueprint, send_from_directory, request, jsonify
from bbs.setting import basedir
from flask import current_app, make_response, abort
from bbs.utils import redirect_back, MyMDStyleExtension
from flask_login import login_required
import markdown

normal_bp = Blueprint('normal', __name__, url_prefix='/normal')


@normal_bp.route('/image/<string:path>/<string:filename>/', methods=['GET'])
def get_image(path, filename):
    path = basedir + '/resources/{}/'.format(path)
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


@normal_bp.route('/comment/render-md/', methods=['POST'])
@login_required
def render_md():
    md = request.form.get('md')
    html = markdown.markdown(md, extensions=['markdown.extensions.fenced_code', 'markdown.extensions.tables',
                                             MyMDStyleExtension()])
    print(html)
    return jsonify({'html': html})
