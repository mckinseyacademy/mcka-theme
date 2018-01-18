var modal_form = $('.tile_modal_form');
var in_person_session = modal_form.find('.in_person_session');
var fa_icon = modal_form.find('.fa_icon');
var fa_icon_input = modal_form.find('#id_fa_icon')
var webinar = modal_form.find('.webinar');
var start_date = modal_form.find('.start_date');
var selected_tile_type = modal_form.find('#id_tile_type option:selected').text();
var calendar_checkbox = modal_form.find('#id_show_in_calendar');
var tile_checkbox = modal_form.find('#id_show_in_dashboard');
var calendar_fields = modal_form.find('.calendar_fields');
var tile_fields = modal_form.find('.tile_fields');

adjust_by_tile_type(selected_tile_type);
adjust_for_calendar_entry(calendar_checkbox);
adjust_for_tile_entry(tile_checkbox);

modal_form.find('#id_show_in_calendar').change(function(){
  adjust_for_calendar_entry($('#id_show_in_calendar'));
});

modal_form.find('#id_show_in_dashboard').change(function(){
  adjust_for_tile_entry($('#id_show_in_dashboard'));
});

modal_form.find('#id_tile_type').change(function(){
  selected_tile_type = $('#id_tile_type option:selected').text();
  adjust_by_tile_type(selected_tile_type);
});

modal_form.find('#id_start_date').on('click', function(){
  $('#tileFormSubmit').attr('disabled',false);
});

modal_form.find('#id_publish_date').on('click', function(){
  $('#tileFormSubmit').attr('disabled',false);
});

modal_form.find('#id_end_date').on('click', function(){
  $('#tileFormSubmit').attr('disabled',false);
});

function adjust_for_calendar_entry(calendar_checkbox){
  if (calendar_checkbox.is(':checked')){

    calendar_fields.slideDown('fast');
    $("#id_start_date").prop('required',true);
    $("#id_end_date").prop('required',true);
  } else {
    calendar_fields.slideUp('fast');
    $("#id_start_date").prop('required',false);
    $("#id_end_date").prop('required',false);
  }
}

function adjust_for_tile_entry(tile_checkbox){
  if (tile_checkbox.is(':checked')){
    tile_fields.slideDown('fast');
  } else {
    tile_fields.slideUp('fast');
  }
}

function adjust_by_tile_type(selected_tile_type) {
  if (selected_tile_type.trim() == gettext('Course')) {
    fa_icon.hide();
    fa_icon_input.val('');
  }
  else {
    fa_icon.show();
  }

  if (selected_tile_type.trim() == gettext('In Person Session')) {
    in_person_session.show();
  } else {
    in_person_session.hide();
  }
}
