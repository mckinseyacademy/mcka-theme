var learnerdashboardId = ($('#replace-calendar').data("learner-dashboard-id"));

$(document).ready(function() {
  var headers = {
    'X-CSRFToken': $.cookie('apros_csrftoken')
  }
  $.ajax({
    headers: headers,
    dataType: 'json',
    data: {
      lesson_link: $('#course-lessons').data('course-url'),
      tile_id: $('#course-lessons').data('tile-id'),
    },
    type: 'POST',
    url: '/learnerdashboard/bookmark_lesson/' + learnerdashboardId + '/'
  });
});
