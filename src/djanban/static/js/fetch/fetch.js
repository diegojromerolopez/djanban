$(document).ready(function(){

    $("#fetch_form").submit(function(){
        $("#fetch_button").prop( "disabled", true );
        $("#fetch_button .fa").show();
        $("#fetch_button").after("<div>Fetching in progress, please wait...</div>");
        return true;
    });

});