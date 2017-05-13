$(document).ready(function(){

    $("#sync_form").submit(function(){
        $("#sync_button").prop( "disabled", true );
        $("#sync_button").after("<div>Synchronization in progress, please wait...</div>");
        return true;
    });

});