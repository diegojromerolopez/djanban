$(document).ready(function(){
   // Multiselectors height
   $("select[multiple]#id_members").attr("size",$("select[multiple]#id_members option").length);
   $("select[multiple]#id_labels").attr("size",$("select[multiple]#id_labels option").length);

   // If there are no labels in the selector, hide it
   if($("#id_labels option").length == 0){
        $(".field-labels-container").hide();
   }

});