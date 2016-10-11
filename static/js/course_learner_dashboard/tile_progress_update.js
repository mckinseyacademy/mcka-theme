$(function(){

  var moduleUrl = $.xblock.location.pathname;

  $.xblock.getRuntime().listenTo('xblock-rendered submit', function(event, data) {
    $(document).ajaxComplete(function() {
      updateTileProgress();
    });
  });

  function updateTileProgress(){
    $.ajax({
      type: 'GET',
      url: moduleUrl
    });
    $(document).unbind("ajaxComplete");
  }
});
