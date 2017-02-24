$(document).ready(function(){

    $(".red_card").hide();
    $(".orange_card").hide();
    $(".yellow_card").hide();

    $(".red_cards_title").click(function(){
        $(".red_card").toggle();
    });

    $(".orange_cards_title").click(function(){
        $(".orange_card").toggle();
    });

    $(".yellow_cards_title").click(function(){
        $(".yellow_card").toggle();
    });

});