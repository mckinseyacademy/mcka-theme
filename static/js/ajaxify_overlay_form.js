
// submits forms via ajax and re-renders the html
function ajaxify_overlay_form(overlaySelector, formSelector, callback) {
  $(overlaySelector).on('submit', formSelector, function(e) {
    e.preventDefault();
    var form = $(this);

    form.find(':submit').prop('disabled', true);
    $.ajax({
      method: 'POST',
      url: form.attr('action'),
      data: form.serialize()
    })
    .done(function(data, status, xhr) {
      var contentType = xhr.getResponseHeader('content-type') || '';
      if (contentType.indexOf('json') > -1 && data.redirect) {
        window.location.href = data.redirect;
      }
      else {
        if($('.new-theme').length && overlaySelector == '#reset-password') {
          form.html($(data).find('form').html());
        } else {
          form.parent().html(data);
        }
        if (callback !== undefined) {
          callback();
        }
        form.find(':submit').prop('disabled', false);
      }
    });
  });
}
