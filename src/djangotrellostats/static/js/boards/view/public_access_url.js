$(document).ready(function(){

    $("#public_access textarea").click(function(){
        $(this).select();
        document.execCommand("copy");
    });

});