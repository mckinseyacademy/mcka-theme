
// submits forms via ajax and re-renders the html
function ajaxify_overlay_form(overlay, formSelector) {
  overlay.on('submit', formSelector, function(e) {
    var form = $(this);
    e.preventDefault();

    form.find(':submit').attr('disabled', 'disabled');

    var xhr = $.ajax({
      method: 'POST',
      url: form.attr('action'),
      data: form.serialize()
    })
    .done(function(data, status, xhr) {
      var contentType = xhr.getResponseHeader('content-type') || '';
      if (contentType.indexOf('json') > -1 && data.redirect)
        window.location.href = data.redirect;
      else
        form.parent().html(data);

      form.find(':submit').removeAttr('disabled'); });
  });
}
