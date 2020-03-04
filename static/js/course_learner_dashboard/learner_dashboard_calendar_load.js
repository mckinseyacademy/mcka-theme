var opened = false;

var learnerdashboardId = ($('#replace-calendar').data("learner-dashboard-id"));

$('#open-calendar').click(function() {
  if (!opened) {

    $('.ld-nav ul>li.calendar a').addClass('dome-active');

    var headers = {
      'X-CSRFToken': $.cookie('apros_csrftoken')
    };

    $.ajax({
      headers: headers,
      type: 'GET',
      url: '/learnerdashboard/' + learnerdashboardId + '/calendar',
      success : function(data) {
        opened = true;
        $('#replace-calendar').html(data.html);

      },
      error: function(xhr, status, error) {
        var err = eval("(" + xhr.responseText + ")");
        console.log (err);
      }
    });
  }
  else {
    $('#replace-calendar').empty();
    opened = false;
    $('.ld-nav ul>li.calendar a').removeClass('dome-active');

  }
});

function nextPrevCalendar(param) {
  var headers = {
    'X-CSRFToken': $.cookie('apros_csrftoken')
  }

  $.ajax({
    headers: headers,
    type: 'GET',
    url: 'learnerdashboard/' + learnerdashboardId + '/calendar',
    data: param,
    success : function(data) {
      opened = true;
      $('#replace-calendar').html(data.html);
    },
    error: function(xhr, status, error) {
      var err = eval("(" + xhr.responseText + ")");
      console.log (err);
    }
  });
}
