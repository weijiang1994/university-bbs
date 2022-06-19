"""
# coding:utf-8
@Time    : 2020/12/16
@Author  : jiangwei
@File    : user.py
@Desc    : user
@Software: PyCharm
"""
import datetime
import os

from sqlalchemy import or_, and_
from sqlalchemy.sql.expression import func
from sqlalchemy.sql.expression import func
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from bbs.models import User, Notification, Post, Comments, PrivateMessage, BlockUser, LoginLog, UserCoinDetail, UserCoin
from bbs.forms import EditUserForm, CropAvatarForm, ChangePasswordForm
from bbs.extensions import db, avatars
from bbs.setting import basedir
from bbs.utils import get_md5, get_upload_img_limit, is_jpg, is_png
from bbs.decorators import user_permission_required
from bbs.constants import COIN_OPERATE_TYPE, COIN_DETAIL_TYPE

user_bp = Blueprint('user', __name__, url_prefix='/user/')


@user_bp.route('/index/<user_id>/', methods=['GET', 'POST'])
@login_required
@user_permission_required
def index(user_id):
    form = EditUserForm()
    user = User.query.get_or_404(user_id)
    if form.validate_on_submit():
        slogan = form.slogan.data
        website = form.website.data
        location = form.location.data
        username = form.user_name.data
        nickname = form.nickname.data
        user.nickname = nickname
        user.username = username
        user.slogan = slogan
        user.website = website
        user.location = location
        db.session.commit()
        flash('资料编辑成功!', 'success')
        return redirect(url_for('.index', user_id=user_id))
    form.user_email.data = user.email
    form.user_name.data = user.username
    form.nickname.data = user.nickname
    form.website.data = user.website
    form.slogan.data = user.slogan
    form.location.data = user.location
    notices = get_notices_counts()
    contacts = get_contact_counts()
    return render_template('frontend/user/user-index.html', user=user, form=form, notices=notices, contacts=contacts)


def get_notices_counts():
    notices = Notification.query.filter(Notification.read == 0, Notification.receive_id == current_user.id). \
        order_by(Notification.timestamp.desc()).all()
    return notices


def get_contact_counts():
    contacts = PrivateMessage.query.filter(PrivateMessage.receiver_id == current_user.id,
                                           PrivateMessage.receiver_status == 0).all()
    return contacts


@user_bp.route('/mark-all-notify/<user_id>')
@login_required
@user_permission_required
def mark_all_notify(user_id):
    Notification.query.filter(Notification.receive_id == user_id,
                              Notification.read == 0).update({Notification.read: 1})
    db.session.commit()
    flash('操作成功！', 'success')
    return redirect(url_for('.notifications', user_id=user_id))


@user_bp.route('/mark-notifications/<notify_id>/')
@login_required
def mark_notification(notify_id):
    notify = Notification.query.filter_by(id=notify_id).first()
    if notify.read:
        notify.read = 0
        flash('消息标记为未读成功!', 'success')
    else:
        notify.read = 1
        flash('消息标记为已读成功!', 'success')
    db.session.commit()
    return redirect(request.referrer)


@user_bp.route('/notifications/<user_id>/')
@login_required
@user_permission_required
def notifications(user_id):
    user = User.query.get_or_404(user_id)
    notices = get_notices_counts()
    contacts = get_contact_counts()
    page = request.args.get('page', default=1, type=int)
    per_page = current_app.config['BBS_PER_PAGE']
    pagination = Notification.query.filter(Notification.receive_id == user_id, Notification.read == 1).paginate(
        page=page,
        per_page=per_page)
    read_notices = pagination.items
    return render_template('frontend/user/user-notification-read.html', user=user, notices=notices,
                           read_notices=read_notices, tag=pagination.total > per_page, contacts=contacts,
                           pagination=pagination)


@user_bp.route('notification-unread/<user_id>/')
@login_required
@user_permission_required
def unread(user_id):
    user = User.query.get_or_404(user_id)
    notices = get_notices_counts()
    contacts = get_contact_counts()
    page = request.args.get('page', default=1, type=int)
    per_page = current_app.config['BBS_PER_PAGE']
    pagination = Notification.query.filter(Notification.receive_id == user_id, Notification.read == 0).paginate(
        page=page,
        per_page=per_page)
    unread_notices = pagination.items
    return render_template('frontend/user/user-notification-unread.html', user=user, notices=notices,
                           unread_notices=unread_notices, tag=pagination.total > per_page, contacts=contacts,
                           pagination=pagination)


@user_bp.route('/contacts/read-message/<user_id>', methods=['POST'])
@login_required
@user_permission_required
def read_private_message(user_id):
    sender_id = request.form.get('senderID').split('person')[-1] if request.form.get("senderID") else None
    PrivateMessage.query.filter(
        PrivateMessage.sender_id == sender_id,
        PrivateMessage.receiver_status == 0,
        PrivateMessage.receiver_id == user_id
    ).update(
        {PrivateMessage.receiver_status: 1})

    person = User.query.get_or_404(sender_id)

    # 获取当前未读消息数量,更新侧边栏
    unread_count = PrivateMessage.query.filter(
        PrivateMessage.receiver_id == user_id,
        PrivateMessage.receiver_status == 0).count()

    # 更新通知为已读
    Notification.query.filter(Notification.send_user == person.username,
                              Notification.receive_id == current_user.id).update({Notification.read: 1})
    db.session.commit()
    return {'code': 200, 'msg': '读取消息成功！', 'unread': unread_count}


@user_bp.route('/delete-message-records', methods=['POST'])
@login_required
def delete_msg_records():
    person = request.form.get('person')
    pms = PrivateMessage.query.filter(or_(and_(PrivateMessage.sender_id == person,
                                               PrivateMessage.receiver_id == current_user.id),
                                          and_(PrivateMessage.sender_id == current_user.id,
                                               PrivateMessage.receiver_id == person))).all()
    for pm in pms:
        if pm.sender_id == current_user.id:
            pm.sender_status = 2
        else:
            pm.receiver_status = 2
    db.session.commit()
    return {'code': 200, 'msg': '删除记录成功!'}


@user_bp.route('/contacts/<user_id>/')
@login_required
@user_permission_required
def contact(user_id):
    user = User.query.get_or_404(user_id)
    right_senders = []
    person_messages = []
    unread_counts = []

    # 查询所有给用户发送过消息的id
    try:
        # MySQL5.7以后group by必须要指定列所以这里加一个异常捕获
        contact_persons = PrivateMessage.query.with_entities(PrivateMessage.sender_id). \
            filter(PrivateMessage.receiver_id == current_user.id).order_by(PrivateMessage.c_time.desc()). \
            group_by(PrivateMessage.sender_id).all()
    except Exception as e:
        contact_persons = PrivateMessage.query.with_entities(PrivateMessage.sender_id). \
            filter(PrivateMessage.receiver_id == current_user.id).order_by(func.MAX(PrivateMessage.c_time).desc()). \
            group_by(PrivateMessage.sender_id).all()

    for idx, sender_id in enumerate(contact_persons):
        contact_persons[idx] = sender_id[0]

    # 查询用户主动发送的但是对方没有回复的消息
    to_users = PrivateMessage.query. \
        with_entities(PrivateMessage.receiver_id). \
        filter(PrivateMessage.sender_id == current_user.id, PrivateMessage.receiver_id.notin_(contact_persons)). \
        group_by(PrivateMessage.receiver_id).all()

    for idx, receiver_id in enumerate(to_users):
        to_users[idx] = receiver_id[0]

    for cp in contact_persons:
        pms = PrivateMessage.query.filter(or_(and_(PrivateMessage.sender_id == cp,
                                                   PrivateMessage.receiver_id == current_user.id,
                                                   PrivateMessage.receiver_status != 2),
                                              and_(PrivateMessage.sender_id == current_user.id,
                                                   PrivateMessage.receiver_id == cp,
                                                   PrivateMessage.sender_status != 2))).order_by(
            PrivateMessage.c_time).all()

        if pms:
            person_messages.append(pms)
            unread_counts.append(PrivateMessage.query.filter(PrivateMessage.sender_id == cp,
                                                             PrivateMessage.receiver_id == current_user.id,
                                                             PrivateMessage.receiver_status == 0).count())
            right_senders.append(User.query.get_or_404(cp))

    for tu in to_users:
        tos = PrivateMessage.query.filter(PrivateMessage.sender_id == current_user.id,
                                          PrivateMessage.receiver_id == tu,
                                          PrivateMessage.sender_status != 2).order_by(PrivateMessage.c_time).all()
        if tos:
            person_messages.append(tos)
            unread_counts.append(0)
            right_senders.append(User.query.get_or_404(tu))

    notices = get_notices_counts()
    contacts = get_contact_counts()
    return render_template('frontend/user/user-contact.html',
                           user=user,
                           notices=notices,
                           contacts=contacts,
                           person_messages=person_messages,
                           right_senders=right_senders,
                           unread_counts=unread_counts)


@user_bp.route('/look-message/<person_id>')
@login_required
def look_message(person_id):
    person = User.query.get_or_404(person_id)
    pms = PrivateMessage.query. \
        filter(or_(and_(PrivateMessage.sender_id == person_id,
                        PrivateMessage.receiver_id == current_user.id),
                   and_(PrivateMessage.sender_id == current_user.id,
                        PrivateMessage.receiver_id == person_id))). \
        order_by(PrivateMessage.c_time).all()

    # 更新私信为已读
    PrivateMessage.query. \
        filter(PrivateMessage.sender_id == person_id,
               PrivateMessage.receiver_id == current_user.id). \
        update({PrivateMessage.receiver_status: 1})

    # 更新通知消息为已读
    Notification.query.filter(Notification.send_user == person.username,
                              Notification.receive_id == current_user.id).update({Notification.read: 1})
    db.session.commit()
    return render_template('frontend/user/user-contact-phone.html',
                           pms=pms,
                           user=current_user,
                           person=person,
                           receiver_id=person_id)


@user_bp.route('/user-edit/<user_id>/', methods=['GET', 'POST'])
@login_required
@user_permission_required
def edit_avatar(user_id):
    crop_form = CropAvatarForm()
    pwd_form = ChangePasswordForm()
    user = User.query.get_or_404(user_id)
    notices = get_notices_counts()
    contacts = get_contact_counts()
    return render_template('frontend/user/user-avatar.html', user=user, crop_form=crop_form, pwd_form=pwd_form,
                           notices=notices, contacts=contacts, max_size=get_upload_img_limit())


@user_bp.route('/change-password/<user_id>/', methods=['GET', 'POST'])
@login_required
@user_permission_required
def change_password(user_id):
    pwd_form = ChangePasswordForm()
    if pwd_form.validate_on_submit():
        password = pwd_form.password2.data
        current_user.set_password(password)
        db.session.commit()
        flash('密码修改成功！', 'success')
    user = User.query.get_or_404(current_user.id)
    notices = get_notices_counts()
    contacts = get_contact_counts()
    return render_template('frontend/user/user-password.html', pwd_form=pwd_form, user=user, notices=notices,
                           contacts=contacts)


@user_bp.route('/user-privacy-setting/<user_id>/', methods=['GET', 'POST'])
@login_required
@user_permission_required
def privacy_setting(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        post_range = request.form.get('postPrivacy')
        comment_range = request.form.get('commentPrivacy')
        collect_range = request.form.get('collectPrivacy')
        contact_range = request.form.get('contactPrivacy')
        user.post_range_id = post_range
        user.comment_range_id = comment_range
        user.collect_range_id = collect_range
        user.contact_range_id = contact_range
        db.session.commit()
        flash('数据更新成功!', 'success')
    notices = get_notices_counts()
    contacts = get_contact_counts()
    return render_template('frontend/user/user-privacy-setting.html', user=user, notices=notices, contacts=contacts)


@user_bp.route('/upload-avatar/', methods=['POST'])
@login_required
def upload_avatar():
    file = request.files.get('image')
    filebytes = file.read()
    if len(filebytes) > 1024 * 1024 * get_upload_img_limit():
        flash('上传的文件不能大于{}M!'.format(str(get_upload_img_limit())), 'warning')
        return redirect(url_for('.edit_avatar', user_id=current_user.id))

    if not (is_jpg(filebytes) or is_png(filebytes)):
        flash('文件格式不是JPG或者PNG!', 'warning')
        return redirect(url_for('.edit_avatar', user_id=current_user.id))

    filename = get_md5(filebytes.hex())
    upload_path = os.path.join(basedir, 'resources/avatars/raw/', filename)
    if not os.path.exists(upload_path):
        # "x"参数项在文件已存在的情况会出错
        # 防止出现极端情况产生Race Condition的情况下
        # 并行写入同一个文件的可能性 用来当做一个"写互斥锁"
        with open(upload_path, "xb") as f:
            f.write(filebytes)

    current_user.avatar_raw = filename
    db.session.commit()
    return redirect(url_for('.edit_avatar', user_id=current_user.id))


@user_bp.route('/crop-avatar/', methods=['POST'])
@login_required
def crop_avatar():
    x = request.form.get('x')
    y = request.form.get('y')
    w = request.form.get('w')
    h = request.form.get('h')
    if current_user.avatar_raw:
        filename = 'raw/' + current_user.avatar_raw
    else:
        filename = None
    files = avatars.crop_avatar(filename, x, y, w, h)
    current_user.avatar = '/normal/image/avatars/' + files[2]
    db.session.commit()
    return redirect(url_for('.edit_avatar', user_id=current_user.id))


@user_bp.route('/trash-station-post/<user_id>/')
@login_required
@user_permission_required
def trash_station_post(user_id):
    page = request.args.get('page', default=1, type=int)
    per_page = current_app.config['BBS_PER_PAGE']
    pagination = Post.query.filter(Post.author_id == user_id, Post.status_id == 2).paginate(page=page,
                                                                                            per_page=per_page)
    posts = pagination.items
    user = User.query.get_or_404(user_id)
    notices = get_notices_counts()
    contacts = get_contact_counts()
    return render_template('frontend/user/user-trash-post.html', posts=posts, tag=pagination.total > per_page,
                           user=user, pagination=pagination, notices=notices, contacts=contacts)


@user_bp.route('/trash-station-comment/<user_id>/')
@login_required
@user_permission_required
def trash_station_comment(user_id):
    page = request.args.get('page', default=1, type=int)
    per_page = current_app.config['BBS_PER_PAGE']
    pagination = Comments.query.filter(Comments.author_id == user_id, Comments.delete_flag == 1). \
        paginate(page=page, per_page=per_page)
    comments = pagination.items
    user = User.query.get_or_404(user_id)
    notices = get_notices_counts()
    contacts = get_contact_counts()
    return render_template('frontend/user/user-trash-comment.html', comments=comments, pagination=pagination,
                           tag=pagination.total > per_page, user=user, notices=notices, contacts=contacts)


@user_bp.route('/post-recover/<post_id>/')
@login_required
def post_delete_or_recover(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author_id != current_user.id:
        flash('你无权操作!', 'info')
        return redirect(request.referrer)
    if post.status_id == 1:
        post.status_id = 2
    else:
        post.status_id = 1
    db.session.commit()
    flash('帖子状态操作成功!', 'success')
    return redirect(request.referrer)


@user_bp.route('/comment-operator/<comment_id>/')
@login_required
def comment_operator(comment_id):
    comment = Comments.query.get_or_404(comment_id)
    if comment.author_id != current_user.id:
        flash('你无权操作!', 'info')
        return redirect(request.referrer)
    if comment.delete_flag == 1:
        comment.delete_flag = 0
    else:
        comment.delete_flag = 1
    db.session.commit()
    flash('评论状态操作成功！', 'success')
    return redirect(request.referrer)


@user_bp.route('/user-info', methods=['POST'])
@login_required
def get_user_info():
    user_id = request.form.get('userId')
    user = User.query.get_or_404(user_id)
    return {'code': 200, 'username': user.username, 'nickname': user.nickname, 'sender': current_user.id}


@user_bp.route('/send-message', methods=['POST'])
@login_required
def send_message():
    message = request.form.get('message')
    sender_id = request.form.get('senderID')
    send_user = User.query.get_or_404(sender_id)
    receiver_id = request.form.get('receiverID')

    # 检查发送者是否在接收者的黑名单中
    bu = BlockUser.query.filter(BlockUser.user_id == receiver_id,
                                BlockUser.block_user_id == send_user.id).all()
    if bu:
        return {'code': 400, 'msg': '你在该用户的黑名单中,发送私信失败!'}

    pm = PrivateMessage(sender_id=sender_id,
                        receiver_id=receiver_id,
                        content=message)
    db.session.add(pm)
    ntf = Notification(type=1,
                       target_id=pm.id,
                       target_name='用户私信',
                       send_user=send_user.username,
                       receive_id=receiver_id,
                       msg=message)
    db.session.add(ntf)
    db.session.commit()
    return {'code': 200, 'msg': '私信发送成功!'}


@user_bp.route('/block-user', methods=['POST'])
@login_required
def block_user():
    user_id = request.form.get('userId')
    user = User.query.get_or_404(user_id)
    bu = BlockUser(user_id=current_user.id,
                   block_user_id=user.id)
    db.session.add(bu)
    db.session.commit()
    flash('拉黑用户成功！', 'success')
    return {'code': 200}


@user_bp.route('/block-user-list')
@login_required
def block_user_list():
    bus = BlockUser.query.filter_by(user_id=current_user.id).order_by(BlockUser.c_time.desc()).all()
    return render_template('frontend/user/block-user.html', bus=bus, user=current_user)


@user_bp.route('/delete-block-user/<user_id>')
@login_required
def delete_block_user(user_id):
    BlockUser.query.filter(BlockUser.user_id == current_user.id,
                           BlockUser.block_user_id == user_id).delete()
    db.session.commit()
    flash('移出黑名单成功!', 'success')
    return redirect(request.referrer)


@user_bp.route('/login-log')
@login_required
def login_log():
    logs = LoginLog.query.filter_by(user_id=current_user.id).order_by(LoginLog.timestamps.desc())
    return render_template(
        'frontend/user/user-login-log.html',
        logs=logs,
        user=current_user
    )


@user_bp.route('/coin-detail/')
@login_required
def coin_detail():
    uc = UserCoin.query.filter_by(uid=current_user.id).first()
    coin = False
    gold = silver = copper = 0
    if uc:
        coin = True
        gold = int(uc.balance) // 10000
        silver = int(uc.balance) % 10000 // 100
        copper = int(uc.balance) % 100
    page = request.args.get('page', 1)
    per_page = request.args.get('size', 20)
    pagination = UserCoinDetail.query.filter_by(uid=current_user.id).order_by(
        UserCoinDetail.timestamps.desc()).paginate(
        page=page,
        per_page=per_page
    )
    total = pagination.total
    uc_detail = pagination.items
    return render_template(
        'frontend/user/user-coin-detail.html',
        tag=total > per_page,
        uc_detail=uc_detail,
        user=current_user,
        gold=gold,
        silver=silver,
        copper=copper,
        coin=coin,
        pagination=pagination,
        COIN_OPERATE_TYPE=COIN_OPERATE_TYPE,
        COIN_DETAIL_TYPE=COIN_DETAIL_TYPE
    )
