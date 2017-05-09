$(document).ready(function(){

    $(".delete_comment").click(function(){
        var $delete_form = $(this).parents("form");
        $.confirm({
            title: 'Delete comment',
            content: 'Confirm you really want to delete the comment',
            confirm: function(){
                $delete_form.submit();
            },
            cancel: function(){
                //
            }
        });
        return false;
    });


});
