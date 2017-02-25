$(document).ready(function(){

    /** Copy to clipboard functionality */
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

    /** Adding coping to clipboard functionality to each export button, prefetching the data from the server */
    $(".export_daily_spent_times").each(function(index){
        var $this = $(this);
        $.get($this.attr("href"), function(csv){
            $this.after("<span class='csv' style='display:none;'>"+csv+"</span>");
            $("<a href='javascript:void(0);' class='btn btn-primary' title='Copy to clipboard'>Copy to clipboard</a>").insertAfter($this).click(function(){
                    copy_to_clipboard($this.siblings(".csv").html());
               });
            });
    });

    /** Changing the order of the months ASC or DESC */
    $("#toggle_month_order").click(function(){
        $(this).find("span.fa").toggle();
        var $table = $("#daily_spent_times")
        var $months = $table.find("tbody.month");
        $table.html("");
        $table.append($months.get().reverse());
    });

    $("#toggle_month_order > .asc").hide();
    $("#toggle_month_order > .desc").show();

    /* We want descendant order by default */
    $("#toggle_month_order").click();

});