$(document).ready(function(){

    function refresh(){
        window.location.reload(true);
        setTimeout(refresh, RELOAD_FREQUENCY * 1000);
    }

    setTimeout(refresh, RELOAD_FREQUENCY * 1000);

});