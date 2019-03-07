var learnerdashboardId = ($('#replace-calendar').data("learner-dashboard-id"));

$('.last_visited').click(function() {

  if ($(this).closest('a').attr('target') == '_blank') {
    $('.bookmark').remove();
    $(this).closest('.learner-program').prepend('<i class="bookmark fa fa-bookmark fa-2x"></i>');
  }
  var headers = {
    'X-CSRFToken': $.cookie('apros_csrftoken')
  }
  $.ajax({
    headers: headers,
    dataType: 'json',
    data: {tile_id: $(this).data('tile-id')},
    type: 'POST',
    url: '/learnerdashboard/bookmark_tile/' + learnerdashboardId + '/'
  });
});
