$(document).ready(function() {
  var modal_form = $('.milestone_modal_form');
  var dig_content = modal_form.find('.digital_content_type');
  dig_content.hide();
  var submitButton = modal_form.find('#formSubmit');

  modal_form.find('#id_start_date').datepicker();
  modal_form.find('#id_end_date').datepicker();

  modal_form.find('#id_milestone_type').change(function() {
    var selected = $('#id_milestone_type option:selected').text();
    if (selected.trim() == 'Digital Content')
    {
      dig_content.show();
      submitButton.attr('disabled',true);
    }
    else
    {
      dig_content.hide();
      submitButton.attr('disabled',false);
    }
  });

});
