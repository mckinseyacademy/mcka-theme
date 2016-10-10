$(function(){

  moduleUrl = $.xblock.location.pathname;

  $.xblock.getRuntime().listenTo('submit', function(event, data) {
    updateTileProgress();
  });

  $.xblock.getRuntime().listenTo('xblock-rendered', function(event, data) {
    updateTileProgress();
  });

  function updateTileProgress(){
    var headers = {
      'X-CSRFToken': $.cookie('apros_csrftoken')
    }
    $.ajax({
      headers: headers,
      dataType: 'json',
      type: 'GET',
      url: moduleUrl
    });
  }
});
