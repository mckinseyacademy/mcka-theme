$(document).ready(function() {
  $('form input').on( 'input change', function() {
    $('#formSubmit').attr('disabled',false);
  });
  $('form select').on( 'change', function() {
    $('#formSubmit').attr('disabled',false);
  }); 
});
  

