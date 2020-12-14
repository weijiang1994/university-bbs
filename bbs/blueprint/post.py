"""
# coding:utf-8
@Time    : 2020/12/02
@Author  : jiangwei
@mail    : jiangwei1@kylinos.cn
@File    : post.py
@Software: PyCharm
"""
import datetime

from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify, current_app

from bbs.blueprint.normal import to_html
from bbs.models import Post, Collect, PostReport, ReportCate, Comments
from bbs.forms import CreatePostForm, EditPostForm
from flask_login import login_required, current_user
from bbs.extensions import db
from bbs.utils import get_text_plain, get_emoji_url, EMOJI_INFOS

post_bp = Blueprint('post', __name__, url_prefix='/post')


@post_bp.route('/new/', methods=['GET', 'POST'])
@login_required
def new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        title = form.title.data
        cate = form.category.data
        anonymous = form.anonymous.data
        content = form.body.data
        textplain = get_text_plain(content)
        post = Post(title=title, cate_id=cate, content=content, is_anonymous=anonymous, author_id=current_user.id,
                    textplain=textplain)
        db.session.add(post)
        db.session.commit()
        flash('帖子发布成功!', 'success')
        return redirect(url_for('post.read', post_id=post.id))
    return render_template('frontend/new-post.html', form=form)


@post_bp.route('/read/<post_id>/', methods=['GET'])
def read(post_id):
    page = request.args.get('page', default=1, type=int)
    post = Post.query.get_or_404(post_id)
    per_page = current_app.config['BBS_PER_PAGE']
    if current_user.is_authenticated:
        c_tag = Collect.query.filter(Collect.user_id == current_user.id, Collect.post_id == post_id).first()
    else:
        c_tag = None
    pagination = Comments.query.filter(Comments.post_id == post_id, Comments.delete_flag == 0).order_by(
        Comments.timestamps.asc()).paginate(page, per_page=per_page)

    comments = pagination.items
    post.read_times += 1
    db.session.commit()
    return render_template('frontend/read-post.html', post=post, c_tag=c_tag, comments=comments, pagination=pagination,
                           emoji_urls=EMOJI_INFOS, per_page=per_page, page=page)


@post_bp.route('/edit/<post_id>/', methods=['GET', 'POST'])
@login_required
def edit(post_id):
    form = EditPostForm()
    post = Post.query.get_or_404(post_id)
    if form.validate_on_submit():
        title = form.title.data
        ep = Post.query.filter_by(title=title).first()

        # 修改标题不能是其他已经存在帖子的标题
        if ep and ep.id != post.id:
            flash('该帖子标题已经存在', 'danger')
            return redirect(url_for('.edit', post_id=post_id))

        cate = form.category.data
        anonymous = form.anonymous.data
        content = form.body.data
        post.title = title
        post.cate_id = cate
        post.is_anonymous = anonymous
        post.content = content
        db.session.commit()
        flash('帖子编辑成功!', 'success')
        return redirect(url_for('.read', post_id=post_id))

    form.title.data = post.title
    form.body.data = post.content
    form.category.data = post.cate_id
    form.anonymous.data = post.is_anonymous
    return render_template('frontend/edit-post.html', post=post, form=form)


@post_bp.route('/delete/<post_id>/', methods=['GET'])
@login_required
def delete(post_id):
    post = Post.query.get_or_404(post_id)
    post.status_id = 2
    db.session.commit()
    flash('帖子删除成功!', 'success')
    return redirect(url_for('index_bp.index'))


@post_bp.route('/report/', methods=['GET', 'POST'])
@login_required
def report():
    post_id = request.form.get('postId', type=int)
    report_reason = request.form.get('reportReason')
    rep_cate = request.form.get('reportCate')
    cate = ReportCate.query.filter_by(name=rep_cate).first()
    epr = PostReport.query.filter(PostReport.post_id == post_id, PostReport.user_id == current_user.id,
                                  PostReport.flag == 0).first()
    if epr:
        flash('你已经举报过他了,不要再举报啦,人家也是要面子的啦!', 'info')
        return redirect(url_for('.read', post_id=post_id))
    p = PostReport(post_id=post_id, user_id=current_user.id, rep_content=report_reason, report_cate_id=cate.id)
    db.session.add(p)
    db.session.commit()
    flash('举报成功!', 'success')
    return redirect(url_for('.read', post_id=post_id))


@post_bp.route('/like/<post_id>/', methods=['GET'])
@login_required
def like(post_id):
    post = Post.query.get_or_404(post_id)
    post.likes += 1
    db.session.commit()
    return redirect(url_for('.read', post_id=post_id))


@post_bp.route('/unlike/<post_id>/', methods=['GET'])
@login_required
def unlike(post_id):
    post = Post.query.get_or_404(post_id)
    post.unlikes += 1
    db.session.commit()
    return redirect(url_for('.read', post_id=post_id))


@post_bp.route('/collect/<post_id>/')
@login_required
def collect(post_id):
    post_collect(post_id)
    return redirect(url_for('.read', post_id=post_id))


def post_collect(post_id):
    post = Post.query.get_or_404(post_id)
    c = Collect.query.filter(Collect.user_id == current_user.id, Collect.post_id == post_id).first()
    if c:
        post.collects -= 1
        db.session.delete(c)
        db.session.commit()
        flash('取消收藏帖子成功!', 'success')
    else:
        post.collects += 1
        c = Collect(user_id=current_user.id, post_id=post_id)
        db.session.add(c)
        db.session.commit()
        flash('收藏帖子成功!', 'success')


@post_bp.route('/post-comment/', methods=['POST'])
@login_required
def post_comment():
    comment_content = request.form.get('commentContent')
    post_id = request.form.get('postId')
    comment_content = to_html(comment_content)
    com = Comments(body=comment_content, post_id=post_id, author_id=current_user.id)
    post = Post.query.get_or_404(post_id)
    post.update_time = datetime.datetime.now()
    db.session.add(com)
    db.session.commit()
    return jsonify({'tag': 1})


@post_bp.route('/reply-comment/', methods=['POST'])
@login_required
def reply_comment():
    comment_id = request.form.get('comment_id')
    comment_user_id = request.form.get('comment_user_id')
    comment = request.form.get('comment')
    post_id = request.form.get('post_id')
    reply = Comments(body=comment, replied_id=comment_id, author_id=comment_user_id, post_id=post_id)
    db.session.add(reply)
    db.session.commit()
    return jsonify({'tag': 1})


@post_bp.route('/delete-comment/', methods=['GET', 'POST'])
@login_required
def delete_comment():
    if request.method == 'POST':
        comment_id = request.form.get('comm_id')
        com = Comments.query.get_or_404(comment_id)
        com.delete_flag = 1
        db.session.commit()
        flash('评论删除成功!', 'success')
        return jsonify({'tag': 1})


@post_bp.route('/set-anonymous/<post_id>/')
@login_required
def set_anonymous(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author_id != current_user.id and current_user.get_permission() == 'LITTLE':
        flash('你没有该帖子的操作权限!', 'danger')
        return redirect(url_for('profile.index', user_id=current_user.id))
    # 2表示匿名 1表示实名
    if post.is_anonymous == 2:
        post.is_anonymous = 1
        flash('帖子取消匿名成功!', 'success')
    else:
        post.is_anonymous = 2
        flash('帖子设置匿名成功!', 'success')
    db.session.commit()
    return redirect(url_for('profile.index', user_id=current_user.id))
