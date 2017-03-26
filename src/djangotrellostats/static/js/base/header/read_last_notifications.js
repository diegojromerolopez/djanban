$(document).ready(function(){

    $("li.base_components_header_last_notificationshtml").on("hide.bs.dropdown", function(){
        let $a = $(this).find("a.dropdown-toggle");
        let $oldest_notification = $(this).find("li.oldest_notification");
        if($oldest_notification && $oldest_notification.length > 0){
            // Send the oldest notification id to mark all newer notifications as read
            let oldest_notification_id = $oldest_notification.data("notification");
            let url = $a.data('read-notifications-url');
            let make_request_function_name = "make_request__"+$(this).attr("id");

            // Mark all notifications as read
            $.ajax({
                url: url,
                method: 'POST',
                data: {oldest_notification: oldest_notification_id},
                success: function(data, textStatus, jqXHR ) {
                    window[make_request_function_name]();
                }
            });
        }



    });

});