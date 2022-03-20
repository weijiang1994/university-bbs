"""
# coding:utf-8
@Time    : 2020/12/02
@Author  : jiangwei
@File    : forms.py
@Software: PyCharm
"""
from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import StringField, SubmitField, SelectField, BooleanField, TextAreaField, FileField, Label, HiddenField, \
    PasswordField
from wtforms.validators import DataRequired, Length, Regexp, EqualTo, ValidationError
from flask_ckeditor import CKEditorField
from bbs import User
from bbs.models import College, PostCategory, Post


# noinspection PyMethodMayBeStatic
class BaseUserForm(FlaskForm):
    user_name = StringField(u'用户名',
                            validators=[DataRequired(message='用户名不能为空'),
                                        Length(min=1, max=16, message='用户名长度限定在1-16位之间'),
                                        Regexp('^[a-zA-Z0-9_]*$',
                                               message='用户名只能包含数字、字母以及下划线.')],
                            render_kw={'placeholder': '请输入用户名长度1-16之间'})
    nickname = StringField(u'昵称',
                           validators=[DataRequired(message='昵称不能为空'),
                                       Length(min=1, max=20, message='昵称长度限定在1-20位之间')],
                           render_kw={'placeholder': '请输入昵称长度1-20之间'})
    user_email = StringField(u'注册邮箱',
                             render_kw={'placeholder': '请输入注册邮箱', 'type': 'email'})

    submit = SubmitField(u'注册', render_kw={'class': 'btn btn-success btn-xs'})


# noinspection PyMethodMayBeStatic
class EditUserForm(BaseUserForm):
    slogan = StringField(u'签名',
                         render_kw={'placeholder': '签名长度1-40之间'})
    website = StringField(u'个人网站',
                          render_kw={'placeholder': '个人网站长度1-128之间'})
    location = StringField(u'住址',
                           render_kw={'placeholder': '住址长度1-128之间'})

    def __init__(self, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.user_email.label = Label(self.user_email.id, '当前邮箱')
        self.user_email.render_kw = {'disabled': 'true', 'label': '当前邮箱'}
        self.submit.label = Label(self.submit.id, '保存信息')

    def validate_website(self, filed):
        if len(filed.data) > 128:
            raise ValidationError('网站长度必须小于128!')

    def validate_slogan(self, filed):
        if len(filed.data) > 40:
            raise ValidationError('用户签名长度必须小于40！')

    def validate_location(self, filed):
        if len(filed.data) > 128:
            raise ValidationError('用户住址长度必须小于128!')

    def validate_username(self, filed):
        if filed.data != current_user.username and User.query.filter_by(username=filed.data).first():
            raise ValidationError('用户名已经存在了!')

    def validate_nickname(self, filed):
        if filed.data != current_user.nickname and User.query.filter_by(nickname=filed.data).first():
            raise ValidationError('昵称已经存在了!')


# noinspection PyMethodMayBeStatic
class RegisterForm(FlaskForm):
    user_name = StringField(u'用户名',
                            validators=[DataRequired(message='用户名不能为空'),
                                        Length(min=1, max=16, message='用户名长度限定在1-16位之间'),
                                        Regexp('^[a-zA-Z0-9_]*$',
                                               message='用户名只能包含数字、字母以及下划线.')],
                            render_kw={'placeholder': '请输入用户名长度1-16之间'})
    nickname = StringField(u'昵称',
                           validators=[DataRequired(message='昵称不能为空'),
                                       Length(min=1, max=20, message='昵称长度限定在1-16位之间')],
                           render_kw={'placeholder': '请输入昵称长度1-20之间'})
    user_email = StringField(u'注册邮箱',
                             validators=[DataRequired(message='注册邮箱不能为空'),
                                         Length(min=4, message='注册邮箱长度必须大于4')],
                             render_kw={'placeholder': '请输入注册邮箱', 'type': 'email'})
    password = StringField(u'密码',
                           validators=[DataRequired(message='用户密码不能为空'),
                                       Length(min=8, max=40, message='用户密码长度限定在8-40位之间'),
                                       EqualTo('confirm_pwd', message='两次密码不一致')],
                           render_kw={'placeholder': '请输入密码', 'type': 'password'})
    confirm_pwd = StringField(u'确认密码',
                              validators=[DataRequired(message='用户密码不能为空'),
                                          Length(min=8, max=40, message='用户密码长度限定在8-40位之间')],
                              render_kw={'placeholder': '输入确认密码', 'type': 'password'})
    colleges = SelectField(u'学院', choices=[(1, '计算机')])
    submit = SubmitField(u'注册', render_kw={'class': 'source-button btn btn-primary btn-xs mt-2'})

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        cols = College.query.all()
        self.colleges.choices = [(col.id, col.name) for col in cols]

    def validate_user_name(self, filed):
        if User.query.filter_by(username=filed.data).first():
            raise ValidationError('用户名已被注册.')

    def validate_user_email(self, filed):
        if User.query.filter_by(email=filed.data.lower()).first():
            raise ValidationError('邮箱已被注册.')

    def validate_nickname(self, filed):
        if User.query.filter_by(nickname=filed.data).first():
            raise ValidationError('昵称已被注册')


class LoginForm(FlaskForm):
    usr_email = StringField(u'邮箱/用户名', validators=[DataRequired(message='用户名或邮箱不能为空')],
                            render_kw={'placeholder': '请输入邮箱或用户名'})
    password = StringField(u'登录密码',
                           validators=[DataRequired(message='登录密码不能为空'),
                                       Length(min=8, max=40, message='登录密码必须在8-40位之间')],
                           render_kw={'type': 'password', 'placeholder': '请输入用户密码'})
    remember_me = BooleanField(u'记住我')
    submit = SubmitField(u'登录', render_kw={'class': 'source-button btn btn-primary btn-xs'})


class BasePostForm(FlaskForm):
    title = StringField(u'标题', validators=[DataRequired(message='帖子标题不能为空'),
                                           Length(min=1, max=50, message='用户名长度必须在1到50位之间')],
                        render_kw={'class': '', 'rows': 50, 'placeholder': '输入您的帖子标题'})
    category = SelectField(label=u'分区',
                           default=0,
                           coerce=int,
                           render_kw={'id': 'category', 'data-live-search': 'true'})
    anonymous = SelectField(label=u'是否匿名', default=1, choices=[(1, '实名'), (2, '匿名')], coerce=int)
    tags = StringField(u'帖子标签', render_kw={'placeholder': '请输入帖子标签', 'id': 'post-tags'})
    body = CKEditorField('帖子内容', validators=[DataRequired(message='请输入帖子内容')])
    submit = SubmitField(u'发布', render_kw={'class': 'source-button btn btn-primary btn-xs mt-2 text-right'})

    def __init__(self, *args, **kwargs):
        super(BasePostForm, self).__init__(*args, **kwargs)
        categories = PostCategory.query.all()
        self.category.choices = [(cate.id, cate.name) for cate in categories]


# noinspection PyMethodMayBeStatic
class CreatePostForm(BasePostForm):

    def validate_title(self, filed):
        if Post.query.filter_by(title=filed.data).first():
            raise ValidationError('该标题已存在请换一个!')


class EditPostForm(BasePostForm):
    submit = SubmitField(u'保存编辑', render_kw={'class': 'source-button btn btn-danger btn-xs mt-2 text-right'})


class UploadAvatarForm(FlaskForm):
    image = FileField('头像', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png'], '头像文件类型必须为jpg或者png!')
    ])
    submit = SubmitField(u'上传', render_kw={'class': 'btn btn-success'})


class CropAvatarForm(FlaskForm):
    x = HiddenField(u'', render_kw={'hidden': 'hidden'})
    y = HiddenField(u'', render_kw={'hidden': 'hidden'})
    w = HiddenField(u'', render_kw={'hidden': 'hidden'})
    h = HiddenField(u'', render_kw={'hidden': 'hidden'})
    submit = SubmitField(u'更新头像', render_kw={'class': 'btn btn-success'})


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('旧密码', validators=[DataRequired()])
    password = PasswordField('新密码', validators=[
        DataRequired(), Length(8, 128), EqualTo('password2', message='两次密码必须一致!')])
    password2 = PasswordField('确认', validators=[DataRequired()])
    set = SubmitField(u'修改', render_kw={'class': 'btn btn-success'})


class ResetPasswordForm(FlaskForm):
    # email = StringField(u'注册邮箱',
    #                     validators=[DataRequired(message='注册邮箱不能为空'),
    #                                 Length(min=4, message='注册邮箱长度必须大于4')],
    #                     render_kw={'placeholder': '请输入注册邮箱', 'type': 'email'})
    password = PasswordField('新的密码', validators=[
        DataRequired(), Length(8, 128), EqualTo('password2', message='两次密码必须一致!')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    # captcha = StringField(u'验证码',
    #                       validators=[DataRequired(message='验证码不能为空'),
    #                                   Length(min=6, max=6, message='验证码长度错误')],
    #                       )
    submit = SubmitField(u'重置密码', render_kw={'class': 'btn btn-info', 'type': 'submit'})
