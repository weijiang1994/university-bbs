"""
# coding:utf-8
@Time    : 2020/12/11
@Author  : jiangwei
@mail    : jiangwei1@kylinos.cn
@File    : get-emojis.py
@Desc    : 爬虫脚本,爬取www.emojidaquan.com的emoji表情
@Software: PyCharm
"""
from bbs.setting import basedir
import requests
from bs4 import BeautifulSoup

# 需要爬取的emoji链接
html = requests.get('https://www.emojidaquan.com/common-smileys-people-emojis')
bp = BeautifulSoup(html.text, 'html.parser')
imgs = bp.find_all('img')
index = 0
for img in imgs:
    url = img.get('data-original')
    if url:
        index += 1
        filename = url.split('/')[-1]
        # 保存表情
        with open(basedir + 'emojis/{}'.format(filename), 'wb') as f:
            f.write(requests.get(url).content)
        print('抓取了{}个表情!'.format(index))

print('抓取表情完毕,共抓取到{}个emoji表情!'.format(index))
