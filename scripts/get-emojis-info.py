"""
# coding:utf-8
@Time    : 2020/12/11
@Author  : jiangwei
@mail    : jiangwei1@kylinos.cn
@File    : get-emojis-info.py
@Desc    : 获取爬取的emojis文件名,生成对应的元组信息
@Software: PyCharm
"""
import os
from bbs.setting import basedir

"""
1.需要生成emoji信息的路径
2.从emojidaquan上爬下来的表情命名方式都是name_desc.png方式命名的
"""
destination_dir = basedir + '/test/emojis/'
emoji_infos = []

for root, dirs, files in os.walk(destination_dir):
    for file in files:
        e0 = file
        e1 = file.split('_')[0]
        emoji_infos.append((e0, e1))

print(emoji_infos)
