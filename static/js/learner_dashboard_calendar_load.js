$('#open-calendar').click(function() {

  var headers = {
    'X-CSRFToken': $.cookie('apros_csrftoken')
  }
  $.ajax({
    headers: headers,
    type: 'GET',
    url: '/learnerdashboard/calendar',
    success : function(data) {
      $('#replace-calendar').html(data.html);
    },
    error: function(xhr, status, error) {
      var err = eval("(" + xhr.responseText + ")");
      console.log (err);
    }
  });
});