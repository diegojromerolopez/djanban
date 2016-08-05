$(document).ready(function(){

    $(".select_parameter_in_spent_time_by_day_of_the_week").change(function(){
        var member_id = $("#select_member_in_spent_time_by_day_of_the_week").val();
        var board_id = $("#select_board_in_spent_time_by_day_of_the_week").val();
        var week_of_year = $("#select_week_of_year_in_spent_time_by_day_of_the_week").val();
        //console.log("CHANGE " + member_id+" / "+board_id+" / "+week_of_year);
        var chart_url = SPENT_TIME_BY_DAY_OF_THE_WEEK_CHART_URL.replace("MEMBER", member_id).replace("BOARD", board_id).replace("WEEK_OF_YEAR", week_of_year);
        //console.log(chart_url);
        $("#spent_time_by_day_of_the_week").attr("src", chart_url);
    });

});