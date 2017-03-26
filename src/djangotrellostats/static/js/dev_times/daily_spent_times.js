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
        $this.hide();
        /*
        $.get($this.attr("href"), function(csv){
            $this.after("<span class='csv' style='display:none;'>"+csv+"</span>");
            $("<a href='javascript:void(0);' class='btn btn-primary' title='Copy to clipboard'>Copy to clipboard</a>").insertAfter($this).click(function(){
                    copy_to_clipboard($this.siblings(".csv").html());
               });
            });*/
    });

    /** Changing the order of the months ASC or DESC */
    $("#toggle_month_order").on("click", function(){
        $(this).find("span.fa").toggle();
        var $table_container = $(".months")
        var $months = $table_container.find("table");
        $table_container.html("");
        $table_container.append($months.get().reverse());
    });

    $("#toggle_month_order > .asc").hide();
    $("#toggle_month_order > .desc").show();

    /* We want descendant order by default */
    //$("#toggle_month_order").click();

    /* Send email by ajax */
    $("form#send_daily_spent_times").submit(function(e){
        let url = $(this).attr("action")+"?ajax=1";
        let $form = $(this);
        $form.find("button").prop("disabled", true);
        $form.find(".fa-spinner").show();

        $.ajax({
               type: "POST",
               url: url,
               data: $form.serialize(),
               success: function(data)
               {
                   $form.find("button").prop("disabled", false);
                   $form.find(".fa-spinner").hide();
                   $("#send_daily_spent_times_ok").html("<span>Data sent successfully</span>").show().delay(6000).fadeOut("slow");
               },
               error: function(data){
                    $form.find("button").prop("disabled", false);
                    $form.find(".fa-spinner").hide();
                    $("#send_daily_spent_times_error").html("<span>Data could not be sent successfully</span>").show().delay(6000).fadeOut("slow");
               }
        });

        e.preventDefault()
    });

});