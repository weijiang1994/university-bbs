"""
coding:utf-8
file: constants.py
@time: 2022/4/30 21:34
@desc:
"""
import enum

# Login device type define
PHONE_TYPE = ['iphone', 'android']
COMPUTER_TYPE = ['windows', 'macos', 'linux']
COIN_DETAIL_TYPE = {
    '1': ['发帖', 30],
    '2': ['评论', 5],
    '3': ['签到', 50],
}

COIN_OPERATE_TYPE = {
    1: ['增加', '+', 'text-success'],
    2: ['减少', '-', 'text-danger']
}

COIN_OPERATE_TYPE_DICT = {
    'add': 1,
    'subtract': 2
}


class VoteType(enum.Enum):
    """
    投票类型
    single: 单选
    multiple: 多选
    """
    single = '单选'
    multiple = '多选'
