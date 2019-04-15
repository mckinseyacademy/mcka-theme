$(function () {
  var isSurveyTableFilled = false;
  $(document).on('change', '.new-theme input[type=radio]', function(e) {
    var parent = $(e.target).parents('[data-block-type="pb-mcq"], [data-block-type="adventure"]');
    $(parent).find(".choice-selector").removeClass("selected");
    if (e.target.checked) {
      $(e.target).parent().addClass("selected");
    } else {
      $(e.target).parent().removeClass("selected");
    }
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
    if (e.target.checked) {
      $(e.target).parent().addClass("selected");
    } else {
      $(e.target).parent().removeClass("selected");
    }
  });

  $(document).on('change', '.new-theme input[type=radio]', function (e) {
    var parent = $(e.target).parents('.field-label, .survey-row');
    $(parent).find(".selected").removeClass("selected");
    if (e.target.checked) {
      $(e.target).parent().addClass("selected");
    } else {
      $(e.target).parent().removeClass("selected");
    }
  });

  // Add selected class to selected poll results when appended to DOM
  $(document).on('DOMNodeInserted', '.poll-results-wrapper, .forum-new-post-form, .edit-post-form', function(){
    $(".new-theme .poll-results input[type=radio]:checked, .new-theme input[type=radio]:checked").parent().addClass('selected');
    $(".new-theme .poll-results input[type=radio]:disabled, .new-theme input[type=radio]:disabled").parent().addClass('disabled');
  });

  // assessment block choice
  $(document).on('DOMNodeInserted', '.choices-list, .choice, .choice-selector', function(){
    $(".new-theme .choices-list input[type=radio]:checked, .new-theme input[type=radio]:checked").parent().addClass('selected');
  });
  $(document).on('DOMNodeInserted', '.image-explorer-wrapper', function(){
    $('.image-explorer-hotspot-reveal-body > div').each(function(index, obj){
      if(!$(this).attr('id') || $(this).attr('id').indexOf('ooyala') === -1) {
        $(this).addClass('ie-custom-div')
      }
    })
  });

  // Assessment block checkbox

  $(document).on('DOMNodeInserted', '.choices-list, .choice-selector', function(){
    $(".new-theme .choice-selector input[type=checkbox]:checked").parent().addClass('selected');
  });

  $(document).on('DOMNodeInserted', '.forum-new-post-form', function(){
    $(".new-theme input[type=checkbox]:checked").parent().addClass('selected');
  });

  $(document).on('DOMNodeInserted', '.new-theme .lesson-content', function(){
    if(!isSurveyTableFilled) {
      isSurveyTableFilled = true;
      setTimeout(function(){
        surveyTableLabelPositionsForMobile();
      }, 3000);
    }
  });
});

function surveyTableLabelPositionsForMobile(){
  $('.new-theme .survey-table .survey-option').each(function(index, element){
    var span = $(element).find('.visible-mobile-only').prop('outerHTML');
    $(element).find('.visible-mobile-only').remove();
    $(element).append(span);
    if (index == $('.survey-table .survey-option').length - 1) {
      setTimeout(function () {
        toggleSurveyRadios()
      }, 5000);  
    }
  });
}

function toggleSurveyRadios() {
  $('.new-theme input[type=radio]').each(function (index, el) {
    if (el.checked)
      $(el).parent().addClass('selected');
    if (el.disabled)
      $(el).parent().addClass('disabled');
  });
  $('.new-theme [data-block-type="survey"] input[type=button]').on('click', function (e) {
    // Survey block choice 
    setTimeout(function () { // we have to wait till api responses and updates selected/disabled attributes to input
      $(e.target).prev().find('input[type=radio]').each(function (index, el) {
        if (el.checked)
          $(el).parent().addClass('selected');
        if (el.disabled)
          $(el).parent().addClass('disabled');
      });
    }, 5000);

  });
}