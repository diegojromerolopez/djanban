$(document).ready(function(){

    $("#id_model, #id_board, #id_member").change(function(){
        if($("#id_board").val() != ""){
            let board_name = $( "#id_board option:selected" ).text()
            $("#id_name").val("Board "+board_name+" "+$("#id_model").val()+"-based forecaster");
        }else if($("#id_member").val() != ""){
            let member_name = $( "#id_member option:selected" ).text()
            $("#id_name").val("Member "+member_name+" "+$("#id_model").val()+"-based forecaster");
        }else{
            $("#id_name").val("All boards and members "+$("#id_model").val()+"-based forecaster");
        }
    });

    $("#id_board").change(function(){
        $("#id_member").val("");
    });

    $("#id_member").change(function(){
        $("#id_board").val("");
    });

});