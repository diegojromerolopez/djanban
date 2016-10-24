$(document).ready(function(){

    // On a background color change, the text color is set to its complementary color
    $("#id_background_color").change(function(){
        let background_color = $(this).val()
        let complementary_color = $c.complement('#'+background_color);
        document.getElementById('id_title_color').jscolor.fromString(complementary_color.replace("#", ""))
    });

});