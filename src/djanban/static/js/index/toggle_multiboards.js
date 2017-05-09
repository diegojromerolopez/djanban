$(document).ready(function(){

    $(".list_types-container-wrapper").hide();

    $(".multiboard-title").on("click", function(){
        var multiboard_id = $(this).data("id");
        $(this).children(".fa").toggle();
        $("#list_types-container-wrapper-"+multiboard_id).toggle();
    });

});