$(document).ready(function(){

    function copy_to_clipboard(text) {
          var $temp_element = $("<textarea>");

          $("body").append($temp_element);

          $temp_element.val(text).select();

          try {
            document.execCommand("copy");
          } catch (err) {
            console.log("Some error when copying: " + err);
          }

          $temp_element.remove();
    }

    $(".export_daily_spent_times").each(function(index){
        var $this = $(this);
        $.get($this.attr("href"), function(csv){
            $this.after("<span class='csv' style='display:none;'>"+csv+"</span>");
            $("<a href='javascript:void(0);' class='btn btn-primary' title='Copy to clipboard'>Copy to clipboard</a>").insertAfter($this).click(function(){
                    copy_to_clipboard($this.siblings(".csv").html());
               });
            });
    });

});