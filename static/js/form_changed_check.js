$(function() {
  $('form select, form input').on('keyup change', function(e) {
    $('#formSubmit').attr('disabled',false);
  });
});
