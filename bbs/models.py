"""
coding:utf-8
file: models.py
@author: jiangwei
@contact: jiangwei_1994124@163.com
@time: 2020/11/26 21:45
@desc:
"""
from werkzeug.security import generate_password_hash, check_password_hash
from flask_avatars import Identicon
from bbs.extensions import db, whooshee
import datetime
from flask_login import UserMixin, current_user


class AdminLog(db.Model):
    __tablename__ = 't_admin_log'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    op_id = db.Column(db.INTEGER, db.ForeignKey('t_operator_cate.id'))
    timestamps = db.Column(db.DateTime, default=datetime.datetime.now)
    admin_id = db.Column(db.INTEGER, db.ForeignKey('t_user.id'))
    notes = db.Column(db.TEXT, default='')
    target_id = db.Column(db.INTEGER, db.ForeignKey('t_user.id'))

    op_cate = db.relationship('OperatorCate', back_populates='admin_log')
    admin_user = db.relationship('User', foreign_keys=[admin_id], back_populates='admin_log', lazy='joined')
    target_user = db.relationship('User', foreign_keys=[target_id], back_populates='user_log', lazy='joined')


class Follow(db.Model):
    __tablename__ = 't_follow'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    follower_id = db.Column(db.INTEGER, db.ForeignKey('t_user.id'))
    followed_id = db.Column(db.INTEGER, db.ForeignKey('t_user.id'))

    # 正在关注用户的人
    follower = db.relationship('User', foreign_keys=[follower_id], back_populates='following', lazy='joined')
    # 用户自己正在关注的人
    followed = db.relationship('User', foreign_keys=[followed_id], back_populates='followers', lazy='joined')


@whooshee.register_model('username', 'nickname')
class User(db.Model, UserMixin):
    __tablename__ = 't_user'

    id = db.Column(db.INTEGER, primary_key=True, nullable=False, index=True, autoincrement=True)
    username = db.Column(db.String(40), nullable=False, index=True, unique=True, comment='user name')
    nickname = db.Column(db.String(40), nullable=False, unique=True, comment='user nick name')
    password = db.Column(db.String(256), comment='user password')
    email = db.Column(db.String(128), unique=True, nullable=False, comment='user register email')
    slogan = db.Column(db.String(40), default='')
    website = db.Column(db.String(128), default='', comment="user's website")
    location = db.Column(db.String(128), default='', comment='user location')
    avatar = db.Column(db.String(100), nullable=False, comment='user avatar')
    avatar_raw = db.Column(db.String(100), comment='use avatar raw file')
    following_permission = db.Column(db.BOOLEAN, default=True)
    follower_permission = db.Column(db.BOOLEAN, default=True)
    create_time = db.Column(db.DATETIME, default=datetime.datetime.now)

    status_id = db.Column(db.INTEGER, db.ForeignKey('t_status.id'), default=1)
    college_id = db.Column(db.INTEGER, db.ForeignKey('t_college.id'))
    role_id = db.Column(db.INTEGER, db.ForeignKey('t_role.id'), default=3, comment='user role id default is 3 '
                                                                                   'that is student role')
    post_range_id = db.Column(db.INTEGER, db.ForeignKey('t_range.id'), default=1)
    comment_range_id = db.Column(db.INTEGER, db.ForeignKey('t_range.id'), default=1)
    collect_range_id = db.Column(db.INTEGER, db.ForeignKey('t_range.id'), default=1)
    contact_range_id = db.Column(db.INTEGER, db.ForeignKey('t_range.id'), default=1)
    gender_id = db.Column(db.INTEGER, db.ForeignKey('t_gender.id'), default=1)

    gender = db.relationship('Gender', back_populates='user')
    college = db.relationship('College', back_populates='user')
    role = db.relationship('Role', back_populates='user')
    post = db.relationship('Post', back_populates='user', cascade='all')
    status = db.relationship('Status', back_populates='user')
    collect = db.relationship('Collect', back_populates='user', cascade='all')
    post_report = db.relationship('PostReport', back_populates='user', cascade='all')
    comments = db.relationship('Comments', back_populates='author', cascade='all')
    following = db.relationship('Follow', foreign_keys=[Follow.follower_id], back_populates='follower',
                                lazy='dynamic', cascade='all')
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id], back_populates='followed',
                                lazy='dynamic', cascade='all')

    range_post = db.relationship('Range', back_populates='user_post', foreign_keys=[post_range_id])
    range_comment = db.relationship('Range', back_populates='user_comment', foreign_keys=[comment_range_id])
    range_collect = db.relationship('Range', back_populates='user_collect', foreign_keys=[collect_range_id])
    range_contact = db.relationship('Range', back_populates='user_contact', foreign_keys=[contact_range_id])
    receive_notify = db.relationship('Notification', back_populates='receive_user', cascade='all')

    post_like = db.relationship('PostLike', back_populates='user')
    post_dislike = db.relationship('PostDislike', back_populates='user')

    admin_log = db.relationship('AdminLog', back_populates='admin_user', foreign_keys=[AdminLog.admin_id])
    user_log = db.relationship('AdminLog', back_populates='target_user', foreign_keys=[AdminLog.target_id])

    def set_password(self, pwd):
        self.password = generate_password_hash(pwd)

    def check_password(self, pwd):
        return check_password_hash(self.password, pwd)

    def generate_avatar(self):
        icon = Identicon()
        files = icon.generate(self.username)
        self.avatar = '/normal/image/avatars/' + files[2]

    def get_permission(self):
        return self.role.permission.name

    def is_following(self, user):
        if user.id is None:
            return False
        return self.following.filter_by(followed_id=user.id).first() is not None

    def unfollow(self, user):
        follow = self.following.filter_by(followed_id=user.id).first()
        if follow:
            db.session.delete(follow)
            db.session.commit()

    def follow(self, user):
        if not self.is_following(user):
            follow = Follow(follower=self, followed=user)
            db.session.add(follow)
            db.session.commit()


class College(db.Model):
    __tablename__ = 't_college'

    id = db.Column(db.INTEGER, primary_key=True, nullable=False, autoincrement=True, index=True)
    name = db.Column(db.String(100), nullable=False)
    create_time = db.Column(db.DATETIME, default=datetime.datetime.now)

    user = db.relationship('User', back_populates='college', cascade='all')


class Role(db.Model):
    __tablename__ = 't_role'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True, index=True)
    name = db.Column(db.String(40), nullable=False)
    permission_id = db.Column(db.INTEGER, db.ForeignKey('t_permission.id'), nullable=False)

    user = db.relationship('User', back_populates='role', cascade='all')
    permission = db.relationship('Permission', back_populates='role')


class Permission(db.Model):
    __tablename__ = 't_permission'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True, index=True)
    name = db.Column(db.String(40), nullable=False)

    role = db.relationship('Role', back_populates='permission', cascade='all')


class PostCategory(db.Model):
    __tablename__ = 't_postcate'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    name = db.Column(db.String(40), nullable=False)
    create_time = db.Column(db.Date, default=datetime.date.today)

    post = db.relationship('Post', back_populates='cats', cascade='all')


@whooshee.register_model('title', 'content')
class Post(db.Model):
    __tablename__ = 't_post'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True, index=True)
    title = db.Column(db.String(100), index=True, nullable=False)
    content = db.Column(db.TEXT, nullable=False)
    textplain = db.Column(db.TEXT, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.datetime.now)
    is_anonymous = db.Column(db.INTEGER, default=1, comment='post is anonymous? 2: yes 1: no')
    read_times = db.Column(db.INTEGER, default=0)
    likes = db.Column(db.INTEGER, default=0, comment='like post persons')
    unlikes = db.Column(db.INTEGER, default=0, comment='unlike post persons')
    collects = db.Column(db.INTEGER, default=0, comment='collect post persons')

    cate_id = db.Column(db.INTEGER, db.ForeignKey('t_postcate.id'))
    author_id = db.Column(db.INTEGER, db.ForeignKey('t_user.id'))
    status_id = db.Column(db.INTEGER, db.ForeignKey('t_status.id'), default=1)

    cats = db.relationship('PostCategory', back_populates='post')
    user = db.relationship('User', back_populates='post')
    status = db.relationship('Status', back_populates='post')
    collect = db.relationship('Collect', back_populates='post', cascade='all')
    post_report = db.relationship('PostReport', back_populates='post', cascade='all')
    comments = db.relationship('Comments', back_populates='post', cascade='all')
    post_tag_ship = db.relationship('PostTagShip', back_populates='post')

    post_like = db.relationship('PostLike', back_populates='post')
    post_dislike = db.relationship('PostDislike', back_populates='post')

    def can_delete(self):
        return current_user.id == self.author_id

    def user_liked(self):
        return PostLike.query.filter_by(post_id=self.id, user_id=current_user.id).first()

    def user_unliked(self):
        return PostDislike.query.filter_by(post_id=self.id, user_id=current_user.id).first()


class PostLike(db.Model):
    __tablename__ = 't_post_like'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    post_id = db.Column(db.INTEGER, db.ForeignKey('t_post.id'))
    user_id = db.Column(db.INTEGER, db.ForeignKey('t_user.id'))

    post = db.relationship('Post', back_populates='post_like')
    user = db.relationship('User', back_populates='post_like')

    def is_liked(self):
        return self.user_id == current_user.id


class PostDislike(db.Model):
    __tablename__ = 't_post_dislike'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    post_id = db.Column(db.INTEGER, db.ForeignKey('t_post.id'))
    user_id = db.Column(db.INTEGER, db.ForeignKey('t_user.id'))

    post = db.relationship('Post', back_populates='post_dislike')
    user = db.relationship('User', back_populates='post_dislike')


class Status(db.Model):
    __tablename__ = 't_status'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True, index=True)
    name = db.Column(db.String(40), nullable=False)

    post = db.relationship('Post', back_populates='status', cascade='all')
    user = db.relationship('User', back_populates='status', cascade='all')


class Comments(db.Model):
    __tablename__ = 't_comments'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    body = db.Column(db.Text)
    timestamps = db.Column(db.DATETIME, default=datetime.datetime.now)

    replied_id = db.Column(db.INTEGER, db.ForeignKey('t_comments.id'))
    author_id = db.Column(db.INTEGER, db.ForeignKey('t_user.id'))
    post_id = db.Column(db.INTEGER, db.ForeignKey('t_post.id'))
    delete_flag = db.Column(db.INTEGER, default=0, comment='is it delete? 0: no 1: yes')

    post = db.relationship('Post', back_populates='comments')
    author = db.relationship('User', back_populates='comments')
    replies = db.relationship('Comments', back_populates='replied', cascade='all')
    replied = db.relationship('Comments', back_populates='replies', remote_side=[id])

    def can_delete(self):
        return self.author_id == current_user.id


class Collect(db.Model):
    __tablename__ = 't_collect'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    user_id = db.Column(db.INTEGER, db.ForeignKey('t_user.id'))
    post_id = db.Column(db.INTEGER, db.ForeignKey('t_post.id'))
    timestamps = db.Column(db.DateTime, default=datetime.datetime.now)

    user = db.relationship('User', back_populates='collect', lazy='joined')
    post = db.relationship('Post', back_populates='collect', lazy='joined')


class PostReport(db.Model):
    __tablename__ = 't_post_report'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    post_id = db.Column(db.INTEGER, db.ForeignKey('t_post.id'))
    user_id = db.Column(db.INTEGER, db.ForeignKey('t_user.id'))
    report_cate_id = db.Column(db.INTEGER, db.ForeignKey('t_report_cate.id'))
    rep_content = db.Column(db.String(200), nullable=False, default='')
    flag = db.Column(db.INTEGER, default=0, comment='is it new info flag')
    timestamps = db.Column(db.DateTime, default=datetime.datetime.now)

    post = db.relationship('Post', back_populates='post_report')
    user = db.relationship('User', back_populates='post_report')
    report_cate = db.relationship('ReportCate', back_populates='post_report')


class ReportCate(db.Model):
    __tablename__ = 't_report_cate'

    id = db.Column(db.INTEGER, primary_key=True, nullable=False, autoincrement=True)
    name = db.Column(db.String(40), nullable=False)
    timestamps = db.Column(db.DateTime, default=datetime.datetime.now)

    post_report = db.relationship('PostReport', back_populates='report_cate', cascade='all')


class Range(db.Model):
    __tablename__ = 't_range'

    id = db.Column(db.INTEGER, primary_key=True, nullable=False, autoincrement=True)
    name = db.Column(db.String(40), nullable=False)

    user_post = db.relationship('User', back_populates='range_post', foreign_keys=[User.post_range_id], cascade='all')
    user_comment = db.relationship('User', back_populates='range_comment', foreign_keys=[User.comment_range_id],
                                   cascade='all')
    user_collect = db.relationship('User', back_populates='range_collect', foreign_keys=[User.collect_range_id],
                                   cascade='all')
    user_contact = db.relationship('User', back_populates='range_contact', foreign_keys=[User.contact_range_id],
                                   cascade='all')

    @staticmethod
    def init_range():
        ranges = ['全部', '半年', '一月', '三天', '隐藏', '关注我的']
        for r in ranges:
            db.session.add(Range(name=r))
        db.session.commit()


class Notification(db.Model):
    __tablename__ = 't_notification'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    type = db.Column(db.INTEGER, default=0, comment='notification type 1 post')
    target_id = db.Column(db.INTEGER)
    target_name = db.Column(db.String(200))
    send_user = db.Column(db.String(40))
    receive_id = db.Column(db.INTEGER, db.ForeignKey('t_user.id'))
    msg = db.Column(db.TEXT)
    read = db.Column(db.INTEGER, default=0, comment='is read? 0 no 1 yes')
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)

    receive_user = db.relationship('User', back_populates='receive_notify')


class VerifyCode(db.Model):
    __tablename__ = 't_ver_code'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    val = db.Column(db.INTEGER, nullable=False)
    timestamps = db.Column(db.DateTime, default=datetime.datetime.now)
    expire_time = db.Column(db.DateTime, nullable=False)
    is_work = db.Column(db.Boolean, default=True)
    who = db.Column(db.String(40), nullable=False, comment='this ver code belong who')


class Gender(db.Model):
    __tablename__ = 't_gender'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20), nullable=False)
    timestamps = db.Column(db.DATETIME, default=datetime.datetime.now)

    user = db.relationship('User', back_populates='gender', cascade='all')

    @staticmethod
    def init_gender():
        for g in ['保密', '男', '女']:
            n = Gender(name=g)
            db.session.add(n)


class OperatorCate(db.Model):
    __tablename__ = 't_operator_cate'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True, comment='table column id')
    name = db.Column(db.String(256), nullable=False)
    tag = db.Column(db.INTEGER, default=1, comment='work? 1 yes 0 no')
    timestamps = db.Column(db.DateTime, default=datetime.datetime.now)

    admin_log = db.relationship('AdminLog', back_populates='op_cate', cascade='all')

    @staticmethod
    def init_cate():
        for c in ['锁定用户', '解锁用户', '设置权限', '添加用户', '添加管理员']:
            cate = OperatorCate(name=c)
            db.session.add(cate)
        db.session.commit()


class VisitStatistic(db.Model):
    __tablename__ = 't_visit_statistic'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    times = db.Column(db.INTEGER, default=0)
    day = db.Column(db.Date, default=datetime.date.today, unique=True)


class SearchStatistic(db.Model):
    __tablename__ = 't_search_statistic'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    times = db.Column(db.INTEGER, default=0)
    day = db.Column(db.Date, default=datetime.date.today, unique=True)


class CommentStatistic(db.Model):
    __tablename__ = 't_comment_statistic'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    times = db.Column(db.INTEGER, default=0)
    day = db.Column(db.Date, default=datetime.date.today, unique=True)


class PostStatistic(db.Model):
    __tablename__ = 't_post_statistic'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    times = db.Column(db.INTEGER, default=0)
    day = db.Column(db.Date, default=datetime.date.today, unique=True)


class SearchTraffic(db.Model):
    __tablename__ = 't_search_traffic'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    search_word = db.Column(db.String(40), nullable=False, default='')
    day = db.Column(db.Date, default=datetime.date.today())


class OneSentence(db.Model):
    __tablename__ = 't_one_sentence'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    content = db.Column(db.String(512), default='', nullable=False)
    day = db.Column(db.DATE, default=datetime.date.today())


class Tag(db.Model):
    __tablename__ = 't_post_tag'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), default='', nullable=False)
    c_time = db.Column(db.DateTime, default=datetime.datetime.now)

    post_tag_ship = db.relationship('PostTagShip', back_populates='tag')

    @staticmethod
    def tag_exist(tag_name):
        return Tag.query.filter_by(name=tag_name).first()


class PostTagShip(db.Model):
    __tablename__ = 't_post_tag_ship'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    post_id = db.Column(db.INTEGER, db.ForeignKey('t_post.id'))
    tag_id = db.Column(db.INTEGER, db.ForeignKey('t_post_tag.id'))

    post = db.relationship('Post', back_populates='post_tag_ship')
    tag = db.relationship('Tag', back_populates='post_tag_ship')

    @staticmethod
    def post_in_tag(post_id, tag_id):
        return PostTagShip.query.filter(PostTagShip.post_id == post_id,
                                        PostTagShip.tag_id == tag_id).first()

    @staticmethod
    def find_post_tag(post_id):
        return PostTagShip.query.filter(post_id == post_id)
