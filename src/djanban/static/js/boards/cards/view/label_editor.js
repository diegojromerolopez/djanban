$(document).ready(function(){

    $(".card-labels form").hide();

    $("<a id='edit_labels_button' class='btn btn-primary' href='javascript:void(0);'>Edit labels</a>").insertAfter(".card-labels .card-labels-list").click(function(){
        $(".card-labels form").toggle();
        if($(".card-labels form").is(":visible")){
            $(this).html("Cancel label edition");
            $(this).attr("title", "Cancel label edition");
        }else{
            $(this).html("Edit labels");
            $(this).attr("title", "Edit labels");
        }
    });


    $("button.change_labels").click(function(){
        var $change_labels_form = $(this).parents("form");
        $.confirm({
            title: "Change card labels",
            content: "Confirm you really want to change this card labels",
            confirm: function(){
                $change_labels_form.submit();
            },
            cancel: function(){
                //
            }
        });
        return false;
    });

});