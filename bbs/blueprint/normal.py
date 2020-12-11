"""
# coding:utf-8
@Time    : 2020/12/02
@Author  : jiangwei
@mail    : jiangwei1@kylinos.cn
@File    : normal.py
@Software: PyCharm
"""
from bleach import clean, linkify
from flask import Blueprint, send_from_directory, request, jsonify
from markdown import markdown

from bbs.setting import basedir
from flask import current_app, make_response, abort
from bbs.utils import redirect_back, MyMDStyleExtension, EMOJI_INFOS
from flask_login import login_required
import re

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
    html = to_html(md)
    return jsonify({'html': html})


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
