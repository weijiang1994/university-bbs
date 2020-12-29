"""
# coding:utf-8
@Time    : 2020/12/29
@Author  : jiangwei
@mail    : jiangwei1@kylinos.cn
@File    : email.py
@Desc    : email
@Software: PyCharm
"""
from threading import Thread

from bbs.extensions import mail
from flask_mail import Message
from flask import current_app, render_template


def async_send_mail(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to_mail, subject, template, **kwargs):
    message = Message(current_app.config['BBS_MAIL_SUBJECT_PRE'] + subject,
                      recipients=[to_mail],
                      sender=current_app.config['MAIL_USERNAME'])
    message.body = render_template(template + '.txt', **kwargs)
    message.html = render_template(template + '.html', **kwargs)
    th = Thread(target=async_send_mail, args=(current_app._get_current_object(), message))
    th.start()
    return th
