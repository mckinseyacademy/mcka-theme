$(function() {
  $('form').each(function(){
    $(this).data('serialized', $(this).serialize())
  })
  .on('change input', function(){
    $(this).find('input:submit, button:submit').prop('disabled', $(this).serialize() == $(this).data('serialized'));
  }).find('input:submit, button:submit').prop('disabled', true);
});