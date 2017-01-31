$(function(){

  var moduleUrl = $.xblock.location.pathname;

  $.xblock.getRuntime().listenTo('xblock-rendered', function(event, data) {
    updateTileProgress();
    $(data).find(".input-main, .submit, #group-project-completion-checkmark").click(function () {
      $(document).ajaxComplete(function() {
        updateTileProgress();
      });
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
