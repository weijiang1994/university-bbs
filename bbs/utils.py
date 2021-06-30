"""
# coding:utf-8
@Time    : 2020/12/02
@Author  : jiangwei
@mail    : jiangwei1@kylinos.cn
@File    : utils.py
@Software: PyCharm
"""
import re
from markdown import extensions
from markdown.treeprocessors import Treeprocessor
from bbs.setting import basedir
import hashlib
import psutil
import yaml
import os

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


def get_audit():
    yl = yaml.load(open(os.path.join(basedir, 'conf/config.yml')))
    return yl.get('admin').get('audit')


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
    return random.randint(134299, 873242)


class MyMDStyleTreeProcessor(Treeprocessor):
    def run(self, root):
        for child in root.getiterator():
            if child.tag == 'table':
                child.set("class", "table table-bordered table-hover")
            elif child.tag == 'img':
                child.set("class", "img-fluid d-block img-pd10")
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
