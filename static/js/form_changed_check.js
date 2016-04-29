$(document).ready(function() {
   $('form select, form input').change(function() {
        $('#formSubmit').attr('disabled',false);
   });
});
