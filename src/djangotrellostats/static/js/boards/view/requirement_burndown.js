$(document).ready(function(){

    $("#select_requirement_for_requirement_burndown").change(function(){
        var requirement_burndown = $(this).val();
        var chart_url = REQUIREMENT_BURNDOWN_URL.replace("REQUIREMENT", requirement_burndown);
        console.log(chart_url);
        $("#requirement_burndown").attr("src", chart_url);
        $("#requirement_burndown").parent().attr("href", chart_url);
    });

});