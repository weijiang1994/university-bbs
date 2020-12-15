function follow(userId) {
    $.ajax({
        type: "post",
        url:"/profile/follow/"+userId+'/',
        success:function (res) {
            if (res.tag === 1){
                window.location.reload()
            }
        }
    })
}

function unfollow(userId) {
    $.ajax({
        type: "post",
        url:"/profile/unfollow/"+userId+'/',
        success:function (res) {
            if (res.tag === 1){
                window.location.reload()
            }
        }
    })
}