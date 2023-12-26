"""
# coding:utf-8
@Time    : 2022/01/18
@Author  : jiangwei
@File    : task.py
@Desc    : task
@email   : qq804022023@gmail.com
@Software: PyCharm
"""
from bbs.models import VisitStatistic, CommentStatistic, PostStatistic, SearchStatistic, IPRegion
from bbs.extensions import db, aps, rd
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


# @aps.task('interval', id='save_ip_detail', seconds=60)
@aps.task('date')
@log_traceback(logger)
def save_ip_detail():
    keys = rd.keys(pattern='*-detail')
    for key in keys:
        ip = key.split('-')[0]
        db_ip = IPRegion.query.filter_by(ip=ip)
        try:
            ip_detail = rd.hmget(key, keys=['country', 'countryCode', 'region', 'regionName', 'city', 'lat',
                                            'lon', 'timezone', 'org', 'isp', 'zip', 'as', 'status'])
        except Exception as e:
            logger.error('Get ip detail from redis error: %s' % e)
            continue
        logger.debug('Get ip detail from redis: %s' % ip_detail)
        if ip_detail[-1] != 'success':
            continue
        ip_data = {
            'ip': ip,
            'country': ip_detail[0],
            'country_code': ip_detail[1],
            'region': ip_detail[2],
            'region_name': ip_detail[3],
            'city': ip_detail[4],
            'lat': ip_detail[5],
            'lon': ip_detail[6],
            'timezone': ip_detail[7],
            'org': ip_detail[8],
            'isp': ip_detail[9],
            'zip': ip_detail[10],
            'as_': ip_detail[11],
            'last_update': datetime.datetime.now(),
        }
        if not db_ip.first():
            ip_region = IPRegion(**ip_data)
            db.session.add(ip_region)
            db.session.commit()
            rd.delete(key)
        else:
            # 更新数据库中的ip信息
            db_ip.update(**ip_data)
            rd.delete(key)
            db.session.commit()
