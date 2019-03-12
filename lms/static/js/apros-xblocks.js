$(function () {
  var isSurveyTableFilled = false;
  $(document).on('change', '.new-theme input[type=radio]', function(e) {
    var parent = $(e.target).parents('[data-block-type="pb-mcq"]');
    $(parent).find(".choice-selector").removeClass("selected");
    $(e.target).parent().addClass("selected");
  });

  $(document).on('change', '.new-theme [data-block-type="pb-mrq"] input[type="checkbox"], .new-theme .post-options input[type="checkbox"]', function (e) {
    if (e.target.checked) {
      $(e.target).parent().addClass("selected");
    } else {
      $(e.target).parent().removeClass("selected");
    }
  });

  $(document).on('change', '.new-theme input[type=radio]', function (e) {
    var parent = $(e.target).parents('[data-block-type="poll"]');
    $(parent).find(".poll-input-container").removeClass("selected");
    $(e.target).parent().addClass("selected");
  });

  $(document).on('change', '.new-theme input[type=radio]', function (e) {
    var parent = $(e.target).parents('.field-label');
    $(parent).find(".selected").removeClass("selected");
    $(e.target).parent().addClass("selected");
  });

  // Add selected class to selected poll results when appended to DOM
  $(document).on('DOMNodeInserted', '.poll-results-wrapper, .forum-new-post-form, .edit-post-form', function(){
    $(".new-theme .poll-results input[type=radio]:checked, .new-theme input[type=radio]:checked").parent().addClass('selected');
  });

  // assessment block choice
  $(document).on('DOMNodeInserted', '.choices-list, .choice, .choice-selector', function(){
    $(".new-theme .choices-list input[type=radio]:checked, .new-theme input[type=radio]:checked").parent().addClass('selected');
  });

  // Assessment block checkbox

  $(document).on('DOMNodeInserted', '.choices-list, .choice-selector', function(){
    $(".new-theme .choice-selector input[type=checkbox]:checked").parent().addClass('selected');
  });

  $(document).on('DOMNodeInserted', '.forum-new-post-form', function(){
    $(".new-theme input[type=checkbox]:checked").parent().addClass('selected');
  });

  $(document).on('DOMNodeInserted', '.lesson-content', function(){
    if(!isSurveyTableFilled) {
      isSurveyTableFilled = true;
      setTimeout(function(){
        surveyTableLabelPositionsForMobile();
      }, 3000);
    }
  });
});

function surveyTableLabelPositionsForMobile(){
  $('.survey-table .survey-option').each(function(index, element){
    var span = $(element).find('.visible-mobile-only').prop('outerHTML');
    $(element).find('.visible-mobile-only').remove();
    $(element).append(span);
  });
}
