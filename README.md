# university-bbs
一个使用Flask+Bootstrap4搭建的校园论坛(理论上可以是任何论坛doge~)

当前版本正在开发当中,目前上线的版本仅仅包含有基础功能!

[在线演示地址](http://bbs.2dogz.cn)

## 配置环境
在终端中进入项目根目录，然后输入下面的命令，通过pip安装相关的第三方依赖
```bash
pip install -r requirments.txt -i https://pypi.douban.com/simple
```

## 创建数据库
通过可视化工具或者命令行的方式都可以创建数据库，Windows用户可以现在Navicat通过可视化界面来创建数据库，
相关设置如下图所示

![image.png](https://7.dusays.com/2021/04/14/2b7ee15a6628d.png)

如果是`Linux`用户的话，可以通过如下命令创建数据库
```bash
sudo mysql
create database bbs charset utf8 collate utf8_general_ci
```

## 配置相关文件
在根目录中新建`.env`文件，在文件中键入如下内容
```ini
DATABASE_USER= # 设置你自己的数据库连接用户名
DATABASE_PWD= # 设置你自己的数据库连接用户登录密码
DATABASE_HOST=127.0.0.1
DATABASE_PORT=3306
SECRET_KEY='dev'
MAIL_SERVER='smtp.qq.com'
MAIL_USERNAME= # 设置邮箱名
MAIL_PASSWORD= # 设置邮箱秘钥,不是登录密码而是申请SMTP时自动生成的秘钥
```

在`config`目录根据`config.exmpale.yml`文件复制一份改名为`config.yml`，然后根据实际情况修改当中的内容，yaml文件内容如下图

![yaml.png](https://gitee.com/weiijang/image-bed/raw/master/images/image.png)
> 这一步的操作需要在本机先安装好`MySQL`数据库或者`Mariadb`数据。

## 初始化数据库表
激活虚拟环境后，在终端中输入如下命令初始化数据库表
```bash
flask init
```
在这一步中，如果一直提示没有init命令，可以先使用flask run 运行应用并
访问网页，然后再到终端中执行该命令
```bash
flask superuser
```
通过上面的命令添加管理员账号，根据终端提示输入管理员账号的相关信息!

## 启动
万事俱备，在终端中输入下面的命令，启动我们的应用
```bash
flask run
```

打开浏览器，访问`http://127.0.0.1:5000`就可以看到下面的页面啦~

![image.png](https://7.dusays.com/2021/04/14/9546a7e1b7358.png)

## 后台管理系统

> 此仓库为项目的前台系统，面向的是用户端！如需后台管理端，请点击下方连接跳转！后台管理系统采用前后端分离模式开发！(vue2.x + flask1.x)

- [后台管理系统前端](https://github.com/weijiang1994/bbs-admin-frontend)

- [后台管理系统后端](https://github.com/weijiang1994/bbs-admin-backend)
  
  