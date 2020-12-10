"""
# coding:utf-8
@Time    : 2020/12/02
@Author  : jiangwei
@mail    : jiangwei1@kylinos.cn
@File    : utils.py
@Software: PyCharm
"""
import re
import markdown
from bleach import clean, linkify
from markdown import extensions
from markdown.treeprocessors import Treeprocessor

try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin

from flask import request, url_for, redirect


def validate_username(username):
    r = re.match('^[a-zA-Z0-9_]*$', username)
    return True if r else False


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def redirect_back(default='index_bp.index', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))


def get_text_plain(html_text):
    from bs4 import BeautifulSoup
    bs = BeautifulSoup(html_text, 'html.parser')
    return bs.get_text()


class MyMDStyleTreeProcessor(Treeprocessor):
    def run(self, root):
        for child in root.getiterator():
            if child.tag == 'table':
                child.set("class", "table table-bordered table-hover")
            elif child.tag == 'img':
                child.set("class", "d-block img-fluid mx-auto")
            elif child.tag == 'blockquote':
                child.set('class', 'blockquote-comment')
            elif child.tag == 'p':
                child.set('class', 'mt-0 mb-0 p-break')
            elif child.tag == 'pre':
                child.set('class', 'mb-0')
            elif child.tag == 'h1':
                child.set('class', 'comment-h1')
            elif child.tag == 'h2':
                child.set('class', 'comment-h2')
            elif child.tag == 'h3':
                child.set('class', 'comment-h3')
            elif child.tag in ['h4', 'h5', 'h6']:
                child.set('class', 'comment-h4')
        return root


# noinspection PyAttributeOutsideInit
class MyMDStyleExtension(extensions.Extension):
    def extendMarkdown(self, md):
        md.registerExtension(self)
        self.processor = MyMDStyleTreeProcessor()
        self.processor.md = md
        self.processor.config = self.getConfigs()
        md.treeprocessors.add('mystyle', self.processor, '_end')
