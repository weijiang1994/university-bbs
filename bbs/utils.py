"""
# coding:utf-8
@Time    : 2020/12/02
@Author  : jiangwei
@File    : utils.py
@Software: PyCharm
"""
import re
import time

from markdown import extensions
from markdown.treeprocessors import Treeprocessor
from bbs.setting import basedir
import hashlib
import psutil
import yaml
import os
import logging
from logging.handlers import RotatingFileHandler
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature
from flask import current_app

try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin

from flask import request, url_for, redirect

EMOJI_INFOS = [[('angry-face_1f620.png', 'angry-face'),
                ('anguished-face_1f627.png', 'anguished-face'),
                ('astonished-face_1f632.png', 'astonished-face'),
                ('baby-angel_1f47c.png', 'baby-angel'),
                ('baby_1f476.png', 'baby'),
                ('broken-heart_1f494.png', 'broken-heart'),
                ('confounded-face_1f616.png', 'confounded-face'),
                ('confused-face_1f615.png', 'confused-face')],
               [('crying-face_1f622.png', 'crying-face'),
                ('disappointed-but-relieved-face_1f625.png', 'disappointed-but-relieved-face'),
                ('disappointed-face_1f61e.png', 'disappointed-face'),
                ('dizzy-face_1f635.png', 'dizzy-face'),
                ('drooling-face_1f924.png', 'drooling-face'),
                ('expressionless-face_1f611.png', 'expressionless-face'),
                ('face-savouring-delicious-food_1f60b.png', 'face-savouring-delicious-food'),
                ('face-screaming-in-fear_1f631.png', 'face-screaming-in-fear')],
               [('face-throwing-a-kiss_1f618.png', 'face-throwing-a-kiss'),
                ('face-with-cold-sweat_1f613.png', 'face-with-cold-sweat'),
                ('face-with-cowboy-hat_1f920.png', 'face-with-cowboy-hat'),
                ('face-with-finger-covering-closed-lips_1f92b.png', 'face-with-finger-covering-closed-lips'),
                ('face-with-head-bandage_1f915.png', 'face-with-head-bandage'),
                ('face-with-look-of-triumph_1f624.png', 'face-with-look-of-triumph'),
                ('face-with-medical-mask_1f637.png', 'face-with-medical-mask'),
                ('face-with-monocle_1f9d0.png', 'face-with-monocle')],
               [('face-with-one-eyebrow-raised_1f928.png', 'face-with-one-eyebrow-raised'),
                ('face-with-open-mouth-and-cold-sweat_1f630.png', 'face-with-open-mouth-and-cold-sweat'),
                ('face-with-open-mouth-vomiting_1f92e.png', 'face-with-open-mouth-vomiting'),
                ('face-with-open-mouth_1f62e.png', 'face-with-open-mouth'),
                ('face-with-rolling-eyes_1f644.png', 'face-with-rolling-eyes'),
                ('face-with-stuck-out-tongue-and-tightly-closed-eyes_1f61d.png',
                 'face-with-stuck-out-tongue-and-tightly-closed-eyes'),
                ('face-with-stuck-out-tongue-and-winking-eye_1f61c.png', 'face-with-stuck-out-tongue-and-winking-eye'),
                ('face-with-stuck-out-tongue_1f61b.png', 'face-with-stuck-out-tongue')],
               [('face-with-tears-of-joy_1f602.png', 'face-with-tears-of-joy'),
                ('face-with-thermometer_1f912.png', 'face-with-thermometer'),
                ('face-without-mouth_1f636.png', 'face-without-mouth'),
                ('fearful-face_1f628.png', 'fearful-face'),
                ('flushed-face_1f633.png', 'flushed-face'),
                ('frowning-face-with-open-mouth_1f626.png', 'frowning-face-with-open-mouth'),
                ('ghost_1f47b.png', 'ghost'), ('girl_1f467.png', 'girl')],
               [('grimacing-face_1f62c.png', 'grimacing-face'),
                ('grinning-face-with-one-large-and-one-small-eye_1f92a.png',
                 'grinning-face-with-one-large-and-one-small-eye'),
                ('grinning-face-with-smiling-eyes_1f601.png', 'grinning-face-with-smiling-eyes'),
                ('grinning-face-with-star-eyes_1f929.png', 'grinning-face-with-star-eyes'),
                ('grinning-face_1f600.png', 'grinning-face'),
                ('heavy-black-heart_2764.png', 'heavy-black-heart'),
                ('hugging-face_1f917.png', 'hugging-face'),
                ('hushed-face_1f62f.png', 'hushed-face')],
               [('imp_1f47f.png', 'imp'),
                ('kissing-face-with-closed-eyes_1f61a.png', 'kissing-face-with-closed-eyes'),
                ('kissing-face-with-smiling-eyes_1f619.png', 'kissing-face-with-smiling-eyes'),
                ('kissing-face_1f617.png', 'kissing-face'), ('loudly-crying-face_1f62d.png', 'loudly-crying-face'),
                ('lying-face_1f925.png', 'lying-face'), ('money-mouth-face_1f911.png', 'money-mouth-face'),
                ('nauseated-face_1f922.png', 'nauseated-face')],
               [('nerd-face_1f913.png', 'nerd-face'),
                ('neutral-face_1f610.png', 'neutral-face'),
                ('pensive-face_1f614.png', 'pensive-face'),
                ('persevering-face_1f623.png', 'persevering-face'),
                ('pouting-face_1f621.png', 'pouting-face'),
                ('relieved-face_1f60c.png', 'relieved-face'),
                ('rolling-on-the-floor-laughing_1f923.png', 'rolling-on-the-floor-laughing'),
                ('serious-face-with-symbols-covering-mouth_1f92c.png', 'serious-face-with-symbols-covering-mouth')],
               [('shocked-face-with-exploding-head_1f92f.png', 'shocked-face-with-exploding-head'),
                ('sleeping-face_1f634.png', 'sleeping-face'), ('sleepy-face_1f62a.png', 'sleepy-face'),
                ('slightly-frowning-face_1f641.png', 'slightly-frowning-face'),
                ('slightly-smiling-face_1f642.png', 'slightly-smiling-face'),
                ('smiling-face-with-halo_1f607.png', 'smiling-face-with-halo'),
                ('smiling-face-with-heart-shaped-eyes_1f60d.png', 'smiling-face-with-heart-shaped-eyes'),
                ('smiling-face-with-horns_1f608.png', 'smiling-face-with-horns')],
               [('smiling-face-with-open-mouth-and-cold-sweat_1f605.png',
                 'smiling-face-with-open-mouth-and-cold-sweat'),
                ('smiling-face-with-open-mouth-and-smiling-eyes_1f604.png',
                 'smiling-face-with-open-mouth-and-smiling-eyes'),
                ('smiling-face-with-open-mouth-and-tightly-closed-eyes_1f606.png',
                 'smiling-face-with-open-mouth-and-tightly-closed-eyes'),
                ('smiling-face-with-open-mouth_1f603.png', 'smiling-face-with-open-mouth'),
                ('smiling-face-with-smiling-eyes-and-hand-covering-mouth_1f92d.png',
                 'smiling-face-with-smiling-eyes-and-hand-covering-mouth'),
                ('smiling-face-with-smiling-eyes_1f60a.png', 'smiling-face-with-smiling-eyes'),
                ('smiling-face-with-sunglasses_1f60e.png', 'smiling-face-with-sunglasses'),
                ('smirking-face_1f60f.png', 'smirking-face')],
               [('sneezing-face_1f927.png', 'sneezing-face'),
                ('thinking-face_1f914.png', 'thinking-face'),
                ('tired-face_1f62b.png', 'tired-face'),
                ('unamused-face_1f612.png', 'unamused-face'),
                ('upside-down-face_1f643.png', 'upside-down-face'),
                ('weary-face_1f629.png', 'weary-face'),
                ('white-frowning-face_2639.png', 'white-frowning-face'),
                ('white-smiling-face_263a.png', 'white-smiling-face')],
               [('winking-face_1f609.png', 'winking-face'),
                ('worried-face_1f61f.png', 'worried-face'),
                ('yellow-heart_1f49b.png', 'yellow-heart'),
                ('zipper-mouth-face_1f910.png', 'zipper-mouth-face')]]

# 用户帖子、评论、收藏可查范围map
PANGU_DATE = '1970-01-01'
TIME_RANGE = {'全部': 1, '半年': 180, '一月': 30, '三天': 3, '隐藏': -1}

yaml_file = basedir + '/conf/config.yml'
fs = open(yaml_file, encoding='utf8')
conf = yaml.load(fs, Loader=yaml.FullLoader)


class Config(object):
    def __init__(self, path=yaml_file):
        """
        constructor
        @param path: path of configure file that you need to read or write
        """
        self.path = path
        self.yaml = None
        self.open()
        self.value = None

    def open(self):
        with open(self.path, encoding='utf8') as f:
            self.yaml = yaml.load(f, Loader=yaml.FullLoader)

    def read(self, keys):
        try:
            if isinstance(keys, str):
                return self.yaml.get(keys)
            if isinstance(keys, list):
                for key in keys:
                    self.yaml = self.yaml.get(key)
                value = self.yaml
                self.open()
                return value
            raise Exception('Error key type')
        except Exception as e:
            raise e

    def write(self, data):
        with open(self.path, 'w', encoding='utf8') as f:
            self.yaml.dump(data, f)


def get_audit():
    yl = yaml.load(open(os.path.join(basedir, 'conf/config.yml')))
    return yl.get('admin').get('audit')


def get_admin_email():
    yl = yaml.load(open(os.path.join(basedir, 'conf/config.yml')))
    return yl.get('admin').get('mail')


def get_upload_img_limit():
    yl = yaml.load(open(os.path.join(basedir, 'conf/config.yml')))
    return yl.get('admin').get('upload-img')


def get_backend_url():
    yl = yaml.load(open(os.path.join(basedir, 'conf/config.yml')))
    return dict(backend=yl.get('admin').get('backend_url'))


def get_emoji_url():
    """
    获取所有表情的url连接
    :return: 所有表情的url链接
    """
    emoji_urls = []
    url = '/static/emojis/{}'
    tmp = []
    for emoji in EMOJI_INFOS:
        for e in emoji:
            tmp.append(url.format(e[0]))
        emoji_urls.append(tmp)
    return emoji_urls


def get_md5(text):
    return hashlib.md5(text.encode()).hexdigest()


def is_jpg(filestream: bytes) -> bool:
    if len(filestream) < 11:
        return False
    if filestream[:4] != b'\xff\xd8\xff\xe0':
        return False
    if filestream[6:11] != b'JFIF\0':
        return False
    return True


def is_png(filestream: bytes) -> bool:
    if len(filestream) < 6:
        return False
    if filestream[0:6] != b'\x89\x50\x4e\x47\x0d\x0a':
        return False
    return True


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


def generate_ver_code():
    import random
    return random.randint(105181, 952511)


class MyMDStyleTreeProcessor(Treeprocessor):
    def run(self, root):
        # from packaging import version
        # import platform
        # if version.parse(platform.python_version()) >= version.parse("3.9.0"):
        #     root_iter = root.iter()
        # else:
        #     root_iter = root.getiterator()

        try:
            root_iter = root.getiterator()
        except AttributeError:
            root_iter = root.iter()

        for child in root_iter:
            if child.tag == 'table':
                child.set("class", "table table-bordered table-hover")
            elif child.tag == 'img':
                child.set("class", "img-fluid d-block img-pd10 pic")
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


def hardware_monitor():
    cpu_per = psutil.cpu_percent()
    me_per = psutil.virtual_memory().percent
    return cpu_per, me_per


def log_util(log_name, log_path, max_size=2 * 1024 * 1024, backup_count=10):
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    logger = logging.getLogger(log_name)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    file_handler = RotatingFileHandler(log_path + '/' + log_name,
                                       maxBytes=max_size,
                                       backupCount=backup_count
                                       )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)
    return logger


def generate_token(user, expire_in=None, **kwargs):
    s = Serializer(current_app.config['SECRET_KEY'], expire_in)
    data = {'id': user.id}
    data.update(**kwargs)
    return s.dumps(data)


def validate_token(user, token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except (SignatureExpired, BadSignature):
        return False

    if user.id != data.get('id'):
        return False

    return True


def deserialize_token(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
        return data
    except (SignatureExpired, BadSignature):
        return None
