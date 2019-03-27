$(function(){

   if ($(window).width() > 992)
   {
       if ($('#learnerDashboardGallery .col-md-4').length > 9)
       {
           $('#learnerDashboardGallery').removeClass('noScrollAppears');
       }

   }


   if ($(window).width() < 1025) {
           $('.gallery.mCustomScrollbar._mCS_1').removeClass('mCustomScrollbar _mCS_1');

   }

});
