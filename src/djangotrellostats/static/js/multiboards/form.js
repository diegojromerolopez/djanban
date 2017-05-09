$(document).ready(function(){
   $("select[multiple]#id_boards").attr("size",$("select[multiple]#id_boards option").length);
   $("select[multiple]#id_members").attr("size",$("select[multiple]#id_members option").length);
});