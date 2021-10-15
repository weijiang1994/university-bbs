"""
# coding:utf-8
@Time    : 2020/12/11
@Author  : jiangwei
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
destination_dir = basedir + '/bbs/static/emojis/'
emoji_infos = []
tmp = None

for root, dirs, files in os.walk(destination_dir):
    tmp = []
    for file in files:
        e0 = file
        e1 = file.split('_')[0]
        tmp.append((e0, e1))
        if len(tmp) == 8:
            emoji_infos.append(tmp)
            tmp = []
emoji_infos.append(tmp)
print(emoji_infos)
