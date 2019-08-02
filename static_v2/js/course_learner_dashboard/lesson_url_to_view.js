$(window).on('load', function() {
  var ldID = ($('#replace-calendar').data("learner-dashboard-id"));
  var tileID = $('#course-lessons').data('tile-id');
  
  if(ldID && tileID){
    var headers = {
    'X-CSRFToken': $.cookie('apros_csrftoken')
    };
    $.ajax({
      headers: headers,
      dataType: 'json',
      data: {
        lesson_link: $('#course-lessons').data('course-url'),
        tile_id: $('#course-lessons').data('tile-id')
      },
      type: 'POST',
      url: '/learnerdashboard/bookmark_lesson/' + ldID + '/'
    });
  }
});
