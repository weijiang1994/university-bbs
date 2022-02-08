"""
# coding:utf-8
@Time    : 2020/12/02
@Author  : jiangwei
@File    : post.py
@Software: PyCharm
"""
import datetime

from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify, current_app
from bbs.blueprint.frontend.normal import to_html
from bbs.models import Post, Collect, PostReport, ReportCate, Comments, Notification, CommentStatistic, PostStatistic, \
    PostCategory, PostLike, PostDislike, Tag, PostTagShip, UserInterest, BlockUser
from bbs.forms import CreatePostForm, EditPostForm
from flask_login import login_required, current_user
from bbs.extensions import db
from bbs.utils import get_text_plain, EMOJI_INFOS, get_audit, get_admin_email
from bbs.decorators import statistic_traffic, post_can_read, record_read
from bbs.email import send_email
from bs4 import BeautifulSoup

post_bp = Blueprint('post', __name__, url_prefix='/post')


@post_bp.route('/new/', methods=['GET', 'POST'])
@login_required
@statistic_traffic(db, PostStatistic)
def new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        title = form.title.data
        cate = form.category.data
        anonymous = form.anonymous.data
        content = form.body.data
        tags = form.tags.data.split(',') if form.tags.data else []
        textplain = get_text_plain(content)
        if get_audit():
            post = Post(title=title, cate_id=cate, content=content, is_anonymous=anonymous, author_id=current_user.id,
                        textplain=textplain, status_id=3)
        else:
            post = Post(title=title, cate_id=cate, content=content, is_anonymous=anonymous, author_id=current_user.id,
                        textplain=textplain, status_id=1)
        db.session.add(post)
        insert_post_tag(post, tags)
        db.session.commit()
        flash('帖子发布成功!', 'success')
        send_email(
            to_mail=get_admin_email(),
            subject='Post Audit',
            template='email/postAudit',
            post=post,
        )
        return redirect(url_for('post.read', post_id=post.id))
    return render_template('frontend/post/new-post.html', form=form)


def insert_post_tag(post, tags):
    for tag in tags:
        if not Tag.tag_exist(tag):
            t = Tag(name=tag)
            db.session.add(t)
        else:
            t = Tag.tag_exist(tag)

        if not PostTagShip.post_in_tag(post.id, t.id):
            db.session.add(PostTagShip(post_id=post.id, tag_id=t.id))


@post_bp.route('/read/<post_id>/', methods=['GET'])
@post_can_read
@record_read
def read(post_id):
    page = request.args.get('page', default=1, type=int)
    post = Post.query.get_or_404(post_id)
    per_page = current_app.config['BBS_PER_PAGE']
    if current_user.is_authenticated:
        is_collect = Collect.query.filter(Collect.user_id == current_user.id, Collect.post_id == post_id).first()
    else:
        is_collect = None
    pagination = Comments.query.filter(Comments.post_id == post_id, Comments.delete_flag == 0).order_by(
        Comments.timestamps.asc()).paginate(page, per_page=per_page)
    p_tags = PostTagShip.find_post_tag(post_id)
    comments = pagination.items
    post.read_times += 1
    db.session.commit()
    return render_template('frontend/post/read-post.html',
                           post=post,
                           c_tag=is_collect,
                           comments=comments,
                           pagination=pagination,
                           emoji_urls=EMOJI_INFOS,
                           per_page=per_page,
                           page=page,
                           p_tags=p_tags)


@post_bp.route('/elite-operator/<post_id>')
@login_required
def elite(post_id):
    post = Post.query.filter_by(id=post_id).first()
    post.is_elite = not post.is_elite
    db.session.commit()
    flash('操作成功！', 'success')
    return redirect(url_for('post.read', post_id=post_id))


@post_bp.route('/cate/<cate_id>/', methods=['GET'])
def post_cate(cate_id):
    page = request.args.get('page', default=1, type=int)
    cate = PostCategory.query.get_or_404(cate_id)
    paginations = Post.query.filter(Post.cate_id == cate_id,
                                    Post.status_id == 1).order_by(Post.update_time.desc()). \
        paginate(per_page=current_app.config['BBS_PER_PAGE'], page=page)
    posts = paginations.items
    return render_template('frontend/post/cate-post.html', posts=posts, cate=cate)


@post_bp.route('/elite/<cate_id>', methods=['GET'])
def elite_post(cate_id):
    page = request.args.get('page', default=1, type=int)
    cate = PostCategory.query.get_or_404(cate_id)
    paginates = Post.query.filter(Post.cate_id == cate_id, Post.is_elite == True).order_by(
        Post.create_time.desc()).paginate(
        per_page=current_app.config['BBS_PER_PAGE'], page=page)
    posts = paginates.items
    return render_template('frontend/post/elite-post.html', posts=posts, cate=cate)


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
        if form.tags.data == ','.join([tag.name for tag in PostTagShip.find_all_tag(post_id)]):
            pass
        else:
            PostTagShip.delete_all_tag(post_id)
            tags = form.tags.data.split(',') if form.tags.data else []
            insert_post_tag(post, tags)

        db.session.commit()
        flash('帖子编辑成功!', 'success')
        return redirect(url_for('.read', post_id=post_id))

    form.title.data = post.title
    form.body.data = post.content
    form.category.data = post.cate_id
    form.anonymous.data = post.is_anonymous
    form.tags.data = ','.join([tag.name for tag in PostTagShip.find_all_tag(post_id)])
    return render_template('frontend/post/edit-post.html', post=post, form=form)


@post_bp.route('/delete/<post_id>/', methods=['GET'])
@login_required
def delete(post_id):
    post = Post.query.get_or_404(post_id)
    if post.can_delete():
        post.status_id = 2
        db.session.commit()
        flash('帖子删除成功!', 'success')
    else:
        flash('不是你的东西,你没有权限删除!', 'danger')
    return redirect(url_for('index_bp.index'))


@post_bp.route('/report/', methods=['GET', 'POST'])
@login_required
def report():
    post_id = request.form.get('postId', type=int)
    report_reason = request.form.get('reportReason')
    rep_cate = request.form.get('reportCate')
    cate = ReportCate.query.filter_by(name=rep_cate).first()
    epr = PostReport.query.filter(PostReport.post_id == post_id,
                                  PostReport.user_id == current_user.id,
                                  PostReport.flag == 0
                                  ).first()
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
    epl = post.user_liked()
    if epl:
        db.session.delete(epl)
        post.likes -= 1
    else:
        pl = PostLike(post_id=post_id, user_id=current_user.id)
        db.session.add(pl)
        post.likes += 1

    db.session.commit()
    return redirect(url_for('.read', post_id=post_id))


@post_bp.route('/unlike/<post_id>/', methods=['GET'])
@login_required
def unlike(post_id):
    post = Post.query.get_or_404(post_id)
    epdl = post.user_unliked()
    if epdl:
        db.session.delete(epdl)
        post.unlikes -= 1
    else:
        pdl = PostDislike(post_id=post_id, user_id=current_user.id)
        db.session.add(pdl)
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
        flash('取消收藏帖子成功!', 'success')
    else:
        post.collects += 1
        c = Collect(user_id=current_user.id, post_id=post_id)
        db.session.add(c)
        flash('收藏帖子成功!', 'success')

    db.session.commit()


@post_bp.route('/post-comment/', methods=['POST'])
@login_required
@statistic_traffic(db, CommentStatistic)
def post_comment():
    comment_content = request.form.get('commentContent')
    post_id = request.form.get('postId')
    post = Post.query.get_or_404(post_id)
    md_text = comment_content
    comment_content = to_html(comment_content)
    soup = BeautifulSoup(comment_content, 'html.parser')
    com = Comments(body=comment_content, post_id=post_id, author_id=current_user.id, text=soup.text, md=md_text)
    # 如果评论帖子用户与发帖用户不为同一人则发送消息通知
    if current_user.id != post.author_id and not BlockUser.query.filter(BlockUser.user_id == post.author_id,
                                                                        BlockUser.block_user_id == current_user.id).all():
        notice = Notification(target_id=post_id, target_name=post.title, send_user=current_user.username,
                              receive_id=post.author_id, msg=comment_content)
        db.session.add(notice)
    post.update_time = datetime.datetime.now()
    db.session.add(com)
    db.session.commit()
    return jsonify({'tag': 1})


@post_bp.route('/reply-comment/', methods=['POST'])
@login_required
@statistic_traffic(db, CommentStatistic)
def reply_comment():
    comment_id = request.form.get('comment_id')
    # 用于处理消息通知
    comment_user_id = request.form.get('comment_user_id')
    comment = request.form.get('comment')
    md_text = comment
    comment = to_html(comment)
    post_id = request.form.get('post_id')
    soup = BeautifulSoup(comment_content, 'html.parser')
    reply = Comments(body=comment, replied_id=comment_id, author_id=current_user.id, post_id=post_id, text=soup.text,
                     md=md_text)
    post = Post.query.get_or_404(post_id)
    if not BlockUser.query.filter(BlockUser.user_id == comment_user_id,
                                  BlockUser.block_user_id == current_user.id).all():
        notice = Notification(target_id=post_id, target_name=post.title, send_user=current_user.username, msg=comment,
                              receive_id=comment_user_id)
        db.session.add(notice)

    db.session.add(reply)
    post.update_time = datetime.datetime.now()
    db.session.commit()

    return jsonify({'tag': 1})


@post_bp.route('/get-comment', methods=['POST'])
@login_required
def get_comment():
    comment_id = request.form.get('commId')
    comment = Comments.query.filter_by(id=comment_id).first()
    return jsonify({
        'code': 200,
        'markdown': comment.md
    })


@post_bp.route('/edit-comment', methods=['POST'])
@login_required
def edit_comment():
    comment_id = request.form.get('commId')
    content = request.form.get('content')
    comment = Comments.query.filter_by(id=comment_id).first()
    comment.md = content
    comment.body = to_html(content)
    soup = BeautifulSoup(content, 'html.parser')
    comment.text = soup.text
    db.session.commit()
    flash('编辑评论成功!', 'success')
    return jsonify({
        'code': 200,
        'message': '编辑评论成功!'
    })


@post_bp.route('/delete-comment/', methods=['GET', 'POST'])
@login_required
def delete_comment():
    if request.method == 'POST':
        comment_id = request.form.get('comm_id')
        com = Comments.query.get_or_404(comment_id)
        if com.can_delete():
            com.delete_flag = 1
            db.session.commit()
            flash('评论删除成功!', 'success')
        else:
            flash('不是你的东西,你没有权限删除!', 'danger')
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


@post_bp.route('/post-tag/<tag_id>/')
def post_tag(tag_id):
    page = request.form.get('page')
    tag = Tag.query.filter_by(id=tag_id).first()
    all_post = PostTagShip.find_all_post(tag_id, page=page, per_page=current_app.config['BBS_PER_PAGE'])
    posts = all_post.items
    return render_template('frontend/post/tag-post.html',
                           posts=posts,
                           tag=tag)


@post_bp.route('/collect-cate/<cate_id>/')
def collect_cate(cate_id):
    tag = Tag.query.get_or_404(cate_id)
    if UserInterest.exist_user_cate(current_user.id, tag.id):
        uit = UserInterest.exist_user_cate(current_user.id, tag.id)
        db.session.delete(uit)
        flash('取消收藏该主题成功!', 'success')
    else:
        db.session.add(UserInterest(user_id=current_user.id, cate_id=tag.id))
        flash('收藏该主题成功!', 'success')
    db.session.commit()
    return redirect(request.referrer)
