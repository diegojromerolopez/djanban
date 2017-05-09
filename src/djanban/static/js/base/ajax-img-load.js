$(document).ready(function(){

    $("img").each(function(){
        let $this = $(this);
        if($this.data("src")){
            $this.hide();
            let src = $this.data("src");
            $this.before("<span class='img-loader-spinner fa fa-spinner fa-spin fa-2x'></span>");
            $this.attr("src", "");
            $.get(src, function(response){
                $this.attr("src", src);
                $this.siblings("span.img-loader-spinner").remove();
                $this.show();
            });
        }
    });

});
