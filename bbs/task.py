"""
# coding:utf-8
@Time    : 2022/01/18
@Author  : jiangwei
@File    : task.py
@Desc    : task
@email   : qq804022023@gmail.com
@Software: PyCharm
"""
from bbs.models import VisitStatistic, CommentStatistic, PostStatistic, SearchStatistic
from bbs.extensions import db, aps
from bbs.setting import basedir
from bbs.decorators import log_traceback
from bbs.utils import log_util
import datetime

log_path = basedir + '/logs/'
logger = log_util(log_name='task.log',
                  log_path=log_path)


@aps.task('cron', id='insert_data2db', day='*', hour='00', minute='00', second='50')
@log_traceback(logger)
def auto_insert_statistics():
    """
    定时任务,每天00:00:50时刻自动向数据库中插入一条数据,如果数据库中存在了则不作任何动作
    """
    logger.debug('Start insert statistic datas.')
    with db.app.app_context():
        date = datetime.date.today()
        visit = VisitStatistic.query.filter_by(day=date).first()
        post = PostStatistic.query.filter_by(day=date).first()
        comment = CommentStatistic.query.filter_by(day=date).first()
        search = SearchStatistic.query.filter_by(day=date).first()

        if not visit:
            vis = VisitStatistic(day=date, times=0)
            db.session.add(vis)

        if not post:
            p = PostStatistic(times=0, day=date)
            db.session.add(p)

        if not comment:
            c = CommentStatistic(day=date, times=0)
            db.session.add(c)

        if not search:
            s = SearchStatistic(day=date, times=0)
            db.session.add(s)
        db.session.commit()
    logger.debug('Finished insert statistic data.')
