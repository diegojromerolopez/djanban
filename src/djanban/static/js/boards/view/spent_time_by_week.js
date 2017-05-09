$(document).ready(function(){

    $("#select_week_of_year_in_spent_time_by_week").change(function(){
        var week_of_year = $(this).val();
        var chart_url = SPENT_TIME_BY_WEEK_CHART_URL.replace("WEEK_OF_YEAR", week_of_year).replace("0000W00", week_of_year);
        console.log(chart_url);
        $("#spent_time_by_week").attr("src", chart_url);
        $("#spent_time_by_week").parent().attr("href", chart_url);
    });

});