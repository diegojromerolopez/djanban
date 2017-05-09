$(document).ready(function(){

    $(".red_card").hide();
    $(".orange_card").hide();
    $(".yellow_card").hide();

    $(".red_cards_title").on("click", function(){
        $(".red_card").toggle();
    });

    $(".orange_cards_title").on("click", function(){
        $(".orange_card").toggle();
    });

    $(".yellow_cards_title").on("click", function(){
        $(".yellow_card").toggle();
    });

});