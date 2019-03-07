$(function(){

   if ($(window).width() < 1025) {
           $('.gallery.mCustomScrollbar._mCS_1').removeClass('mCustomScrollbar _mCS_1');

   }


   if ($(window).width() < 767) {
       $('.dropdown-menu').click(function(e) {
            e.stopPropagation();
        });
       $('a.LDCourse').click(function (event) {
           $(this).attr('href','#');
           event.preventDefault();
           if($('li.drop-open-dashboard')[0] != $(this).parent('li')[0])
           {
               $('li.drop-open-dashboard').children(":first").addClass('dome-c');
               $('li.drop-open-dashboard').children(":first").css("color", primary);

               $('li.drop-open-dashboard').removeClass();
               $(this).parent('li').addClass('drop-open-dashboard');
               $('li.drop-open-dashboard').children(":first").css("color","#000000");
               $('li.drop-open-dashboard').children(":first").removeClass('dome-c');


           }
           else {
               $('li.drop-open-dashboard').children(":first").css("color", primary);
               $('li.drop-open-dashboard').children(":first").addClass('dome-c');
               $('li.drop-open-dashboard').removeClass();
           }
       });
   }
});
