$(document).on('blur input','#login_id', function() {
    $(this).parents('.form-group').addClass('focused');
    $('#login').attr("disabled", false);
});

if($("#login_id").val() !== "")
{
    $("#login_id").parents('.form-group').addClass('focused');
    $('#login').attr("disabled", false);
}

$('#id_email').on('blur input', function() {
   $(this).parents('.form-group').addClass('focused');
   $('#reset-password-submit').attr("disabled", false)
});


window.Apros = {
  models: {},
  collections: {},
  views: {},
  modals: [],
  config: {},
  utils: {},

  initialize: function () {
    var route = window.location.pathname.replace(/\/$/, ''),
      has_push = window.history && window.history.pushState ? true : false,
      use_hash = !has_push && window.location.pathname.indexOf("/discussion") !== -1; // IE9 fix for MCKIN-2927

    $('header[role=banner] nav[role=navigation] a').each(function () {
      if (route.indexOf($(this).attr('href')) > -1) {
        $(this).addClass('selected');
      }
    });
    Backbone.history.start({
      pushState: has_push,
      hashChange: use_hash
    });
  },

  // http://stackoverflow.com/a/901144/882918
  getParameterByName: function (name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
      // location.search is the query string.
      results = regex.exec(location.search);
    return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
  },

  jumpLinkRewriter: function (jump_link) {
    // Used to rewrite a hrefs on Jump to URLs. See JQuery XBlock for more details.
    var course_url = "/courses/" + jump_link.course_id + "/" + jump_link.block_type + "/lessons/jump_to_page/",
      page_url;
    if (jump_link.jump_type === "jump_to") {
      page_url = jump_link.block_id;
    } else {
      if (jump_link.jump_type !== "jump_to_id") {
        console.log("Unknown jump type: " + jump_link.jump_type + " - assuming jump by id");
      }
      page_url = jump_link.block_id;
    }
    return course_url + page_url;
  },

  chainModal: function (order, modal_selector, entry_callback) {
    this.modals.push({
      order: order,
      selector: modal_selector,
      entry_callback: entry_callback
    });
  },

  executeModalChain: function () {
    if (this.modals.length == 0) {
      return;
    }

    var sorted_modals = _.sortBy(this.modals, 'order');
    var chainStart = sorted_modals[0].entry_callback;

    var idx = 0;
    while (sorted_modals[idx + 1]) {
      $(document).on('closed.fndtn.reveal', sorted_modals[idx].selector, sorted_modals[idx + 1].entry_callback);
      idx += 1;
    }
    chainStart();
  }
};

_(Apros).extend(Backbone.Events);

$(function () {
  Apros.initialize();
  /* Javascript to initialise on ready as defined by jquery */

  // Load video overlay based on video url
  $('a[data-video]').on('click', function (e) {
    var video = $(e.currentTarget).data('video'),
      modal = $('#mckinsey_video'),
      player = $('.player-wrapper', modal).empty();

    var iframe_opts = {
      width: '100%',
      height: '100%',
      frameborder: '0'
    };

    switch (true) {
      case /youtube\.com/.test(video):
        var video_id = video.match(/v=([^#\&\?]*)/)[1];
        iframe_opts.src = '//www.youtube.com/embed/' + video_id + '?rel=0';
        $('.player-wrapper').append($('<iframe />', iframe_opts));
        break;
      case /ted\.com/.test(video):
        var video_id = video.match(/([^#\&\?\/]*$)/)[1];
        iframe_opts.src = 'http://embed.ted.com/talks/' + video_id + '.html';
        $('.player-wrapper').append($('<iframe />', iframe_opts));
        break;
      default:
        $('.player-wrapper').append($('<div />', {
          id: 'ooyala_mckinsey'
        }));
        var ooyala = null;
        if (typeof OO === 'undefined') return;
        if ($('body').hasClass('ie8')) {
          OO.ready(function () {
            ooyala = OO.Player.create('ooyala_mckinsey', video, {
              width: '740px',
              height: '425px'
            });
          });
        } else {
          OO.ready(function () {
            ooyala = OO.Player.create('ooyala_mckinsey', video, {
              width: '100%',
              height: '100%'
            });
          });
        }
        modal.data('ooyala', ooyala);

    }
  });

  $(document).on('close.fndtn.reveal', '[data-reveal]', function () {
    var modal = $(this),
      ooyala = modal.data('ooyala');
    if (ooyala) {
      ooyala.destroy();
      modal.removeData('ooyala');
    }
    $('.player-wrapper', modal).empty();
  });

  // Load user profile information on demand
  $('.user-info').on('click', function () {
    if ($('#profile-container .user-profile').length < 1) {
      $('body, .user-info').css('cursor', 'wait');
      $.ajax({
        url: '/accounts/user_profile.html',
        method: 'GET',
        contentType: 'text/html'
      }).done(function (data, status, xhr) {
        if (xhr.status == 278) {
          window.location.href = xhr.getResponseHeader("Location").replace(/\?.*$/, "?next=" + window.location.pathname);
        }
        if (xhr.status == 200) {
          $('body, .user-info').css('cursor', 'inherit');
          $('#profile-container').html(data);

          $('.user-profile .logout a').on('click', function () {
            var href = $(this).attr('href');
            if (href.length > 1) {
              window.location.href = href;
            }
          });
        }
      });
    }
  });

  $('#edit_field_modal').on('submit', 'form', function (e) {
    e.preventDefault();
    var form = $(this);
    var modal = form.parent();
    form.find(':submit').prop('disabled', true);
    $.ajax({
        method: 'POST',
        url: form.attr('action'),
        data: form.serialize()
      })
      .done(function (data, status, xhr) {
        if ($(data).find('.error, .errorlist').length > 0) {
          modal.html(data);
          form.find(':submit').prop('disabled', false);
        } else {
          modal.foundation('reveal', 'close');

          // force user info refresh
          $('#profile-container').empty();
        }
      });
  });

  $('#profile-container').on('closed opened', function () {
    $('.user-info >.fa').toggleClass('fa-sort-asc fa-sort-desc');
  });

  $('.user-info .user-image').on('click', function () {
    if (!$('#profile-container').hasClass('open')) {
      setTimeout(function () {
        Foundation.libs.dropdown.toggle($('.user-info'));
      }, 5);
    }
  });

  $(document).on('click', '.course-name.unavailable, .status.unavailable', function () {
    var generalModal = $('#generalModal');
    var days = $(this).data('numdays');
    if (typeof days == "undefined") {
      courseStr = gettext("Your course hasn't begun yet. ");
    } else {
      var daysText = ngettext("Your course begins in %(days)s day.", "Your course begins in %(days)s days.", days);
      courseStr = interpolate(daysText, {
        "days": days
      }, true);
    }
    generalModal.find('.title').html(gettext("Welcome to McKinsey Academy"));
    var descriptionText = gettext("%(courseStr)s Before the course begins, you can explore" +
      " this site to learn more about what to expect.", courseStr);
    generalModal.find('.description').html(interpolate(descriptionText, {
      "courseStr": courseStr
    }, true));
    $('#generalModal').foundation('reveal', 'open');
  });

  if ($('#unsupported_modal').length) {
    $('[href="/accounts/login"]').on('click', function (e) {
      e.preventDefault();
      $('#unsupported_modal').show().one('click', function (e) {
        $(this).hide();
      });
    });
  }

  if (/iPhone|iPad/i.test(navigator.userAgent)) {
    $('main img').each(function () {
      var el = $(this),
        cnv = document.createElement("canvas"),
        ctx = cnv.getContext("2d"),
        image = new Image();
      image.src = el.attr('src');
      image.onload = function () {
        cnv.width = image.width;
        cnv.height = image.height;
        ctx.drawImage(image, 0, 0);
        el.attr('src', cnv.toDataURL("image/jpeg"));
      }
    });
  }

  var help_video = $('#mk-help-video');
  if (help_video.length && typeof OO !== 'undefined') {
    OO.ready(function () {
      var player = OO.Player.create('mk-help-video', help_video.data('video-id'), {
        width: '100%',
        height: '300px'
      });
      $('#mckinsey_help').data('ooyala_player', player);
    });
  }

  var intro_modal_selector = $('#intro_modal');
  if ($(intro_modal_selector).length && !localStorage.intro_shown && typeof OO !== 'undefined') {
    Apros.chainModal(10, intro_modal_selector, function () {
      $(intro_modal_selector).foundation('reveal', 'open');
      localStorage.intro_shown = true;
    });
  }

  // Load user program menu
  $('.program-bar .program-menu, #learner-dashboard-header .program-menu').on('click', function () {
    if (!$('#program-menu-content').hasClass('open')) {
      $('body, .program-menu').css('cursor', 'wait');
      $.ajax({
        url: '/courses/courses_menu/',
        method: 'GET',
        contentType: 'text/html'
      }).done(function (data, status, xhr) {
        if (xhr.status == 200) {
          $('body, .program-menu').css('cursor', 'inherit');
          $('#program-menu-content').html(data);
        }
      });
    }
  });

  // $(document).on('closed.fndtn.reveal', '[data-reveal]', function () {
  //   var el = $(this),
  //       player = el.data('ooyala_player');
  //   if (player) {
  //     player.pause();
  //   }
  // });
  //
  // if ($.urlParam('modal')) {
  //   var modalId = $.urlParam('modal'),
  //       anchor = $('[data-reveal-id=' + modalId + ']'),
  //       modal_selector = '#' + modalId,
  //       modal = $(modal_selector);
  //   if (anchor.length) {
  //     anchor.click()
  //   } else {
  //     Apros.chainModal(20, modal_selector, function() {
  //       modal.foundation('reveal', 'open');
  //     });
  //   }
  // }
  //
  // $(document).on('opened.fndtn.reveal', '[data-reveal]', function () {
  //   var modal = $(this),
  //       video = $('[data-video-id]', modal);
  //   if (video.length && typeof OO !== 'undefined') {
  //     var width = $('body').hasClass('ie8') ? '460px' : '100%';
  //     OO.ready(function() {
  //       var player = OO.Player.create(video.attr('id'), video.data('video-id'), {width: width, height: '260px'});
  //       modal.data('ooyala_player', player);
  //     });
  //   }
  // });

  // Placeholder fix
  $(document).on('focus', '.placeholdersjs', function () {
    $(this).addClass('focused_placeholder');
  }).on('blur', '.placeholdersjs', function () {
    $(this).removeClass('focused_placeholder');
  });

  $.xblock.getRuntime().listenTo('navigation', function (event, data) {
    var mapping = {
      'lock': 'addClass',
      'unlock': 'removeClass'
    };
    var result = mapping[data.state];
    if (result !== undefined) {
      var arrows = $('.arrowPin');
      arrows[result]('disabled');
    }
  });

  $.xblock.getRuntime().listenTo("xblock.interaction", function (event, data) {
    if (SCORM_SHELL) {
      var interaction_data = {
        "type": "data",
        "course_id": scorm_data.courseId,
        "assessment": {
          "lesson-id": scorm_data.lessonId,
          "module-id": scorm_data.moduleId,
          "attempts-count": data.attempts_count,
          "attempts-max": data.attempts_max,
          "score": data.score
        }
      };
      SendMessageToSCORMShell(JSON.stringify(interaction_data));
    }
  });

  $.xblock.getRuntime().listenTo('xblock-rendered', function (event, rendered_xblock) {
    if (SCORM_SHELL) {
      var counter = 0;
      var progress_tracker = setInterval(function () {
        counter++;

        if (counter > 3)
          clearInterval(progress_tracker);

        SendProgressToScormShell();

      }, 700);
      setTimeout(function () {
        SendGradebookToScormShell();
      }, 300);
      setTimeout(function () {
        SendCompletionToScormShell();
      }, 300);
    }
    $(".new-theme [data-block-type='pb-mrq'] input[type=checkbox]:checked").parent().addClass('selected');
    $(".new-theme [data-block-type='pb-mcq'] input[type=radio]:checked").parent().addClass('selected');
  });

  Apros.executeModalChain();
});

$(document).on('submit', '.editProfileField form', function(e) {

    e.preventDefault();
    var form = $(this);
    var modal = form.closest('.modal');
    modal.find('.invalid-feedback').hide();
    form.find(':submit').prop('disabled', true);
    $.ajax({
      method: 'POST',
      url: form.attr('action'),
      data: form.serialize()
    })
    .done(function(data, status, xhr) {
      if ($(data).find('.error, .errorlist').length > 0) {

        var errorlist = "";
        $($.parseHTML(data)).find('.errorlist').each(function()
        {
          errorlist = errorlist + $(this).html().trim();
        });
        var error = $($.parseHTML(data)).find('.error').text().trim();
        modal.find('.invalid-feedback').html(errorlist);
        modal.find('.invalid-feedback').append(error);
        modal.find('.invalid-feedback').show();
        form.find(':submit').prop('disabled', false);
      }
      else {
        modal.modal('toggle');
        modal.find('.form-group').removeClass('focused');
        form.find(':submit').prop('disabled', false);
        if(form.find('input[name=title]').length)
        {
          $('.roleArea span').addClass('title');
          $('.roleArea span.title').text(form.find('input[name=title]').val());
        }
        else
        {
          let fullName = $('.nameArea span');
          let fName = form.find('input[name=first_name]').val();
          let lName = form.find('input[name=last_name]').val();

          fullName.text(fName + " " + lName);
          fullName.attr('firstname', fName);
          fullName.attr('lastname', lName);

          let initials = fName[0] + lName[0];
          $('.userNameInitials').text(initials.toUpperCase())
        }
        form.find('input[type=text]').val('');

      }
    });
});


$(document).on('show.bs.modal', '.editProfileField', function (e) {

  var form = $(this).find('form');
  if (form.find('input[name=title]').length) {

    var title = $('.roleArea span.title').text();
    if (title != "")
    {
      $(this).find('.form-group').addClass('focused');
      form.find('input[name=title]').val(title);
    }
  } else {

    let fullName = $('.nameArea span');
    if(fullName.length)
    {
      $(this).find('.form-group').addClass('focused');
      form.find('input[name=first_name]').val(fullName.attr('firstname'));
      form.find('input[name=last_name]').val(fullName.attr('lastname'));
    }
  }

});


$(document).ready(function () {
  var isMobile = (/android|webos|iphone|ipad|ipod|blackberry|com.mcka.RNApp|iemobile|opera mini/i.test(navigator.userAgent.toLowerCase()));
  var longPress = 400;
  var delay = null;
  var shown = false;
  var dragging = false;
  var showPopOver = function(e) {
    if (isMobile){
      return
    }

    if ($(this).hasClass('courseRow')){
      $(this).children('.description').css({'opacity': 1, 'visibility': 'visible', 'display': 'block'});
      return;
    }
    $(this).popover('show');
  };
  var hidePopOver = function(e) {
    if (isMobile){
      return
    }

    if ($(this).hasClass('courseRow')){
      $(this).children('.description').css({'opacity': 0, 'visibility': 'hidden', 'display': 'none'});
      return;
    }
    $(this).popover('hide');
  };

  $( '.longTapPopover[data-toggle="popover"], .courseRow:not(.locked)' ).hover(showPopOver, hidePopOver);
  $( '.longTapPopover[data-toggle="popover"]' ).focus(showPopOver);
  $( '.longTapPopover[data-toggle="popover"]' ).focusout(hidePopOver);

  $( '.longTapPopover[data-toggle="popover"], .courseRow:not(.locked)' ).bind('touchmove', function(event){
    dragging = true;
  });

  $( '.longTapPopover[data-toggle="popover"], .courseRow:not(.locked)' ).bind('touchend', function(event){
    if (!shown){
      let self = $(this);
      if (self.hasClass('courseRow') && !dragging){
        self.css('background-color', self.children('.description').css('background-color'));
        self.children('.description').css({'opacity': 0, 'visibility': 'hidden',  'display': 'none'});
      }
      if(self.hasClass('show-hide')){
        var text = $(self).text();
        if (text == 'visibility_off') {
            $(self).text('visibility');
            $(self).siblings("input").attr('type', 'text');
            $(self).attr("data-content", gettext("Hide password"));
        }
        else {
            $(self).text('visibility_off');
            $(self).siblings("input").attr('type', 'password');
            $(self).attr("data-content", gettext("Show password"));
        }
        event.stopPropagation();
        event.preventDefault();
      }
      clearTimeout(delay);
    } else {
      event.stopPropagation();
      event.preventDefault();
    }
    dragging = false;
    shown = false;
  });

  $( '.longTapPopover[data-toggle="popover"], .courseRow:not(.locked)' ).bind('touchstart', function(e){
    shown = false;
    let self = $(this);
    $('.allCoursesList .courseRow').css('background-color', 'white');
    delay = setTimeout(check, longPress);
    function check() {
      if (self.hasClass('courseRow')){
        self.children('.description').css({'opacity': 1, 'visibility': 'visible', 'display': 'block'});
      }else{
        self.popover('show');
      }
      shown = true;
    }
    document.addEventListener('touchstart', function (e) {
      if (self.hasClass('courseRow')){
        self.children('.description').css({'opacity': 0, 'visibility': 'hidden',  'display': 'none'});
        return;
      }
      self.popover('hide');
    });
  });
  $('.lesson-dropdown-holder').on("click", ".dropdown-menu", function (e) {
      $(e.target).parents('*').andSelf().filter('.courseRow.locked').length !== 0 && e.stopPropagation();
  });
});
