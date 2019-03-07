$(function () {
  $(document).on('change', '.new-theme input[type=radio]', function(e) {
    var parent = $(e.target).parents('[data-block-type="pb-mcq"]');
    $(parent).find(".choice-selector").removeClass("selected");
    $(event.target).parent().addClass("selected");
  });

  $(document).on('change', '.new-theme [data-block-type="pb-mrq"] input[type="checkbox"]', function (event) {
    if (event.target.checked) {
      $(event.target).parent().addClass("selected");
    } else {
      $(event.target).parent().removeClass("selected");
    }
  });

  $(document).on('change', '.new-theme input[type=radio]', function (e) {
    var parent = $(e.target).parents('[data-block-type="poll"]');
    $(parent).find(".poll-input-container").removeClass("selected");
    $(event.target).parent().addClass("selected");
  });

  // Add selected class to selected poll results when appended to DOM
  $(document).on('DOMNodeInserted', '.poll-results-wrapper', function(){
    $(".new-theme .poll-results input[type=radio]:checked").parent().addClass('selected');
  })
});
