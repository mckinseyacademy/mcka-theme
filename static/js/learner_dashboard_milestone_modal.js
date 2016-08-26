$(document).ready(function() {

  var modal_form = $('.milestone_modal_form');
  var digital_content = modal_form.find('.digital_content');
  var in_person_session = modal_form.find('.in_person_session');
  var webinar = modal_form.find('.webinar');
  var start_date = modal_form.find('.start_date');

  digital_content.hide();
  in_person_session.hide();
  webinar.hide();
  start_date.hide();

  var submitButton = modal_form.find('#formSubmit');

  modal_form.find('#id_milestone_type').change(function() {
    var selected = $('#id_milestone_type option:selected').text();

    if (selected.trim() == 'Digital Content')
    {
      webinar.hide();
      in_person_session.hide();
      digital_content.show();
      $("label[for='id_start_date']").text('Start date:');
    }

    if (selected.trim() == 'Webinar')
    {
      digital_content.hide();
      in_person_session.hide();
      webinar.show();
      $("label[for='id_start_date']").text('Date/Time:');
    }

    if (selected.trim() == 'In Person Session')
    {
      webinar.hide();
      digital_content.hide();
      in_person_session.show();
      $("label[for='id_start_date']").text('Start date:');
    }

    if (selected.trim() == '---------')
    {
      webinar.hide();
      digital_content.hide();
      in_person_session.hide();
    }
  });
});
