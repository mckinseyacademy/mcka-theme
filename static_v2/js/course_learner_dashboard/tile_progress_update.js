$(function(){

  var moduleUrl = $.xblock.location.pathname;

  $.xblock.getRuntime().listenTo('xblock-rendered', function(event, data) {
    updateTileProgress();
    $(data).find(".input-main, .submit, button.submit, #group-project-completion-checkmark, input.file_upload[type='file']").click(function () {
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
