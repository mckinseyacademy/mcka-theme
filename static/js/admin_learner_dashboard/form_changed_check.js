$('.discover_modal_form select, .discover_modal_form input').on('keyup change', function(e) {
  $('#discoverFormSubmit').attr('disabled',false);
});

$('.tile_modal_form select, .tile_modal_form input').on('keyup change', function(e) {
  $('#tileFormSubmit').attr('disabled',false);
});