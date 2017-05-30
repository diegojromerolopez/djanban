$(document).ready(function(){
   $("select[multiple]#id_members").attr("size",$("select[multiple]#id_members option").length);

   /* Show only the adequate entity selector depending on type */
   $("#id_type").change(function(){
        var $this = $(this);
        $(".field-board-container, .field-multiboard-container, .field-label-container").hide();
        if($this.val() == "board"){
            $(".field-board-container").show();
        }
        else if($this.val() == "multiboard"){
            $(".field-multiboard-container").show();
        }
        else if($this.val() == "label"){
            $(".field-label-container").show();
        }
        else{

        }
   });

   $("#id_type").change();
});