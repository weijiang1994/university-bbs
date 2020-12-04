"""
# coding:utf-8
@Time    : 2020/12/02
@Author  : jiangwei
@mail    : jiangwei1@kylinos.cn
@File    : post.py
@Software: PyCharm
"""
from flask import Blueprint, render_template, flash, redirect, url_for, request
from bbs.models import Post, Collect, PostReport, ReportCate
from bbs.forms import CreatePostForm, EditPostForm
from flask_login import login_required, current_user
from bbs.extensions import db

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
        post = Post(title=title, cate_id=cate, content=content, is_anonymous=anonymous, author_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash('帖子发布成功!', 'success')
        return redirect(url_for('post.read', post_id=post.id))
    return render_template('frontend/new-post.html', form=form)


@post_bp.route('/read/<post_id>/', methods=['GET'])
def read(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user.is_authenticated:
        c_tag = Collect.query.filter(Collect.user_id == current_user.id, Collect.post_id == post_id).first()
    else:
        c_tag = None
    return render_template('frontend/read-post.html', post=post, c_tag=c_tag)


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
    post = Post.query.get_or_404(post_id)
    c = Collect.query.filter(Collect.user_id == current_user.id, Collect.post_id == post_id).first()
    if c:
        post.collects -= 1
        db.session.delete(c)
        db.session.commit()
    else:
        post.collects += 1
        c = Collect(user_id=current_user.id, post_id=post_id)
        db.session.add(c)
        db.session.commit()
    return redirect(url_for('.read', post_id=post_id))

