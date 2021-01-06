// 初始化下拉框选项
function initSelect(form, type){
    $.ajax({
        url:'/normal/init-select/',
        success: function (res){
            let genders = res.data.gender
            let roles = res.data.role
            let colleges = res.data.college
            for (let i=0;i<genders.length;i++){
                document.getElementById("gender").options.add(new Option(genders[i]['name'], genders[i]['id']));
            }
            for (let i=0;i<roles.length;i++){
                switch (type){
                    case 'user':
                        if (!roles[i].name.includes('管理员')){
                            document.getElementById("role").options.add(new Option(roles[i]['name'], roles[i]['id']));
                        }
                        break;
                    case 'admin':
                        if (roles[i].name.includes('管理员')){
                            document.getElementById("role").options.add(new Option(roles[i]['name'], roles[i]['id']));
                        }
                        break;
                }
            }
            for (let i=0;i<colleges.length;i++){
                document.getElementById("college").options.add(new Option(colleges[i]['name'], colleges[i]['id']));
            }
            form.render();
        }
    })
}

// 提交添加user表单
function submitAddUser(form, layer){
    //监听提交
    form.on('submit(addUser)', function(data){
        $.ajax({
            url: '/backend/user/add-user/',
            type: 'post',
            data:{
                username: $("#username").val(),
                nickname: $("#nickname").val(),
                email: $("#email").val(),
                password: $("#password").val(),
                gender: $("#gender").val(),
                role: $("#role").val(),
                college: $("#college").val(),
            },
            success: function (res){
                if (res.tag){
                    let index = parent.layer.getFrameIndex(window.name);
                    parent.layer.close(index);
                    parent.layer.msg(res.info);
                }else {
                    layer.msg(res.info);
                    return false;
                }
            }
        })
    });
}
