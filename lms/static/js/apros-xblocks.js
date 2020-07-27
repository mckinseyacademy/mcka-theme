$(function () {
  $(document).on('DOMNodeInserted', '.drag-container', function() {
    var $div = $(".target-img-wrapper");
    function preventBehavior(e) {
        e.preventDefault();
    };
    var observer = new MutationObserver(function(mutations) {
      mutations.forEach(function(mutation) {
        if (mutation.attributeName === "class") {
          var attributeValue = $(mutation.target).prop(mutation.attributeName);
          if($(mutation.target).hasClass('dragging')) {
            document.addEventListener("touchmove", preventBehavior, {passive: false});
          } else {
            document.removeEventListener("touchmove", preventBehavior);
          }
        }
      });
    });
    observer.observe($div[0], {
      attributes: true
    });
  });


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
  $(document).on('DOMNodeInserted', '.poll-results-wrapper, .lessonOverview, .forum-new-post-form, .edit-post-form', function(){
    $(".new-theme .poll-results input[type=radio]:checked, .new-theme input[type=radio]:checked").parent().addClass('selected');
    $(".new-theme .poll-results input[type=radio]:disabled, .new-theme input[type=radio]:disabled").parent().addClass('disabled');

    //fall back for private results where results are fetched after 1-2 seconds
    setTimeout(function(){
      $(".new-theme input[type=radio]:disabled").parent().addClass('disabled');
    },3000);

    //discussion inline- big heading
    if($(this).find('.discussion-module-header').length > 0) {
      inlineDiscussionLongHeading();
    }
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
    });
  });

    // Top/Bottom Positioning for the Image explorer popovers

    $(document).on('DOMNodeInserted', function () {
        $(".image-explorer-hotspot").on("click", function (e) {
            var topOffset = $(this).offset().top;
            var docHeight = $(document).height();
            var bottomOffset = (docHeight - topOffset);
            if (bottomOffset < 420) {
                $(this).siblings('.image-explorer-hotspot-reveal').css({"bottom": '0', "top": "auto"});
            }
        });

          //popover positioning for MRQ.MCQ when popover height bigger.
          $(function (e) {
              var popHeight = $(".choice-tips-container.with-tips.active .choice-tips").outerHeight();
              if (popHeight > 320) {
                  $(".choice-tips").parent().addClass('toTop');
              }
          });
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

  $(document).mousedown(function(e){
    if($(e.target).hasClass('vjs-menu-content')){
      e.preventDefault();
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

function inlineDiscussionLongHeading() {
  var moduleWidth = $('.discussion-module-header').width();
  $('.discussion-module-header').each(function(){
    $(this).children('.discussion-module-title').css({'display': 'inline'}); // to get actual width
    //if width is more than 65 % move it downwards
    if($(this).children('.discussion-module-title').eq(0).width() / moduleWidth  * 100 > 65){
      $(this).parent('.discussion-module').addClass('long-discussion-heading');
    }
    // else // We will enable for testing, its not required for production.
    //   $(this).parent('.discussion-module').removeClass('long-discussion-heading');
    $(this).children('.discussion-module-title').css({'display': ''}); // rest width
  });
}

// Discussion sticky stopper handling
  $(document).on("DOMNodeInserted", '.new-theme .forum-nav', function(event) {
    let $sticky = $('.forum-nav');
    let $stickyrStopper = $('.sticky-stopper');
    let windowWidth = window.innerWidth;
    if (windowWidth > 1024) {
      if (!!$sticky.offset()) { // make sure ".sticky" element exists
        let generalSidebarHeight = $sticky.innerHeight();
        let stickyTop = $sticky.offset().top;
        let stickOffset = 10;
        let stickyStopperPosition = $stickyrStopper.offset().top;
        let stopPoint = stickyStopperPosition - generalSidebarHeight + 10000;
        let diff = stopPoint + stickOffset;

        $(window).scroll(function () { // scroll event
          let windowTop = $(window).scrollTop(); // returns number

          if (stopPoint < windowTop) {
            $sticky.css({
              position: 'absolute',
              top: diff,
            });
          } else if (stickyTop < windowTop + stickOffset) {
            $sticky.css({
              position: 'fixed',
              top: stickOffset,
            });
          } else {
            $sticky.css({
              position: 'absolute',
              top: 'initial',
            });
          }
        });

      }
    }
  });
  
