$(function(){

   if ($(window).width() < 576) {
       $('.gallery.mCustomScrollbar._mCS_1').removeClass('mCustomScrollbar _mCS_1');
       $('.dropdown-menu').click(function(e) {
            e.stopPropagation();
        });
       $('a.LDCourse').click(function (event) {
           $(this).attr('href','#');
           event.preventDefault();
           if($('li.drop-open-dashboard')[0] != $(this).parent('li')[0])
           {
               $('li.drop-open-dashboard').removeClass();
               $(this).parent('li').addClass('drop-open-dashboard');

           }
           else {
               $('li.drop-open-dashboard').removeClass();
           }
       });
   }
});
