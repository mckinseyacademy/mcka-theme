var opened = false;

$('#open-calendar').click(function() {
  if (!opened) {

    var headers = {
      'X-CSRFToken': $.cookie('apros_csrftoken')
    }

    $.ajax({
      headers: headers,
      type: 'GET',
      url: '/learnerdashboard/calendar',
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
});

function nextPrevCalendar(param) {
  var headers = {
    'X-CSRFToken': $.cookie('apros_csrftoken')
  }

  $.ajax({
    headers: headers,
    type: 'GET',
    url: '/learnerdashboard/calendar',
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