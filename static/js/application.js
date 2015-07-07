window.Apros = {
  models: {},
  collections: {},
  views: {},

  initialize: function() {
    var route     = window.location.pathname.replace(/\/$/, ''),
        has_push  = window.history && window.history.pushState ? true : false,
        use_hash  = !has_push && window.location.pathname.indexOf("/discussion") !== -1; // IE9 fix for MCKIN-2927

    $('header[role=banner] nav[role=navigation] a').each(function(){
      if(route.indexOf($(this).attr('href')) > -1){
        $(this).addClass('selected');
      }
    });
    Backbone.history.start({pushState: has_push, hashChange: use_hash});
  },

  jumpLinkRewriter: function(jump_link){
    // Used to rewrite a hrefs on Jump to URLs. See JQuery XBlock for more details.
    var course_url = "/courses/" + jump_link.course_id + "/" + jump_link.block_type + "/lessons/jump_to_page/",
        page_url;
    if (jump_link.jump_type === "jump_to") {
      page_url = jump_link.block_id;
    }
    else {
      if (jump_link.jump_type !== "jump_to_id") {
        console.log("Unknown jump type: " + jump_link.jump_type + " - assuming jump by id");
      }
      page_url = "i4x://" + jump_link.course_id + "/vertical/" + jump_link.block_id;
    }
    return course_url + page_url;
  }
};

_(Apros).extend(Backbone.Events);

$(function(){
  Apros.initialize();
  /* Javascript to initialise on ready as defined by jquery */

  // Load video overlay based on video url
  $('a[data-video]').on('click', function(e) {
    var video   = $(e.currentTarget).data('video'),
        modal   = $('#mckinsey_video'),
        player  = $('.player-wrapper', modal).empty();

    var iframe_opts = {
      width:        '100%',
      height:       '100%',
      frameborder:  '0'
    };

    switch (true) {
      case /youtube\.com/.test(video):
        var video_id    = video.match(/v=([^#\&\?]*)/)[1];
        iframe_opts.src = '//www.youtube.com/embed/' + video_id + '?rel=0';
        $('.player-wrapper').append($('<iframe />', iframe_opts));
        break;
      case /ted\.com/.test(video):
        var video_id    = video.match(/([^#\&\?\/]*$)/)[1];
        iframe_opts.src = 'http://embed.ted.com/talks/' + video_id + '.html';
        $('.player-wrapper').append($('<iframe />', iframe_opts));
        break;
      default:
        $('.player-wrapper').append($('<div />', {id: 'ooyala_mckinsey'}));
        var ooyala = null;
        if (typeof OO === 'undefined') return;
        if ($('body').hasClass('ie8')) {
          ooyala = OO.Player.create('ooyala_mckinsey', video, {width: '740px', height: '425px'});
        } else {
          ooyala = OO.Player.create('ooyala_mckinsey', video, {width: '100%', height: '100%'});
        }
        modal.data('ooyala', ooyala);

    }
  });

  $(document).on('close.fndtn.reveal', '[data-reveal]', function () {
    var modal   = $(this),
        ooyala  = modal.data('ooyala');
    if (ooyala) {
      ooyala.destroy();
      modal.removeData('ooyala');
    }
    $('.player-wrapper', modal).empty();
  });

  // Load user profile information on demand
  $('.user-info').on('click', function(){
    if($('#profile-container .user-profile').length < 1){
      $('body, .user-info').css('cursor', 'wait');
      $.ajax({
            url: '/accounts/user_profile.html',
            method: 'GET',
            contentType: 'text/html'
          }).done(function(data, status, xhr) {
            if (xhr.status == 278) {
              window.location.href = xhr.getResponseHeader("Location").replace(/\?.*$/, "?next="+window.location.pathname);
            }
            if(xhr.status == 200){
              $('body, .user-info').css('cursor', 'inherit');
              $('#profile-container').html(data);

              $('.user-profile .logout a').on('click', function(){
                var href = $(this).attr('href');
                if(href.length > 1){
                  window.location.href = href;
                }
              });
            }
          });
    }
  });

  $('#edit_field_modal').on('submit', 'form', function(e) {
    e.preventDefault();
    var form = $(this);
    var modal = form.parent();
    form.find(':submit').prop('disabled', true);
    $.ajax({
      method: 'POST',
      url: form.attr('action'),
      data: form.serialize()
    })
    .done(function(data, status, xhr) {
      if ($(data).find('.error, .errorlist').length > 0) {
        modal.html(data);
        form.find(':submit').prop('disabled', false);
      }
      else {
        modal.foundation('reveal', 'close');

        // force user info refresh
        $('#profile-container').empty();
      }
    });
  });

  $('#profile-container').on('closed opened', function(){
    $('.user-info >.fa').toggleClass('fa-sort-asc fa-sort-desc');
  });

  $('.user-info .user-image').on('click', function(){
    if (!$('#profile-container').hasClass('open')) {
      setTimeout(function(){
        Foundation.libs.dropdown.toggle($('.user-info'));
      }, 5);
    }
  });

  $('.course-name.unavailable, .status.unavailable').on('click', function(){
    var generalModal = $('#generalModal');
    var days = $(this).data('numdays');
    if(typeof days == "undefined"){
      courseStr = "Your course hasn't begun yet. ";
    }
    else{
      days = (days > 1) ? days + " days" : days + " day";
      courseStr = "Your course begins in " + days + ". "
    }
      generalModal.find('.title').html("Welcome to McKinsey Academy");
      generalModal.find('.description').html(courseStr +
      "Before the course begins, you can explore this site to learn more about what to expect.");
      $('#generalModal').foundation('reveal', 'open');
  });

  if ($('#unsupported_modal').length) {
    $('[href="/accounts/login"]').on('click', function(e) {
      e.preventDefault();
      $('#unsupported_modal').show().one('click', function(e){
        $(this).hide();
      });
    });
  }

  if (/iPhone|iPad/i.test(navigator.userAgent)) {
    $('main img').each(function(){
      var el  = $(this),
          cnv = document.createElement("canvas"),
          ctx = cnv.getContext("2d"),
          image = new Image();
      image.src = el.attr('src');
      image.onload = function() {
        cnv.width = image.width;
        cnv.height = image.height;
        ctx.drawImage(image,0,0);
        el.attr('src', cnv.toDataURL("image/jpeg"));
      }
    });
  }

  var help_video = $('#mk-help-video');
  if (help_video.length && typeof OO !== 'undefined') {
    var player = OO.Player.create('mk-help-video', help_video.data('video-id'), {width: '100%', height: '300px'});
    $('#mckinsey_help').data('ooyala_player', player);
  }

  var intro_modal = $('#intro_modal');
  if (intro_modal.length && !localStorage.intro_shown && typeof OO !== 'undefined') {
    intro_modal.foundation('reveal', 'open');
    localStorage.intro_shown = true;
  }

  $(document).on('closed.fndtn.reveal', '[data-reveal]', function () {
    var el = $(this),
        player = el.data('ooyala_player');
    if (player) {
      player.pause();
    }
  });

  if ($.urlParam('modal')) {
    var modalId = $.urlParam('modal'),
        anchor = $('[data-reveal-id=' + modalId + ']'),
        modal = $('#' + modalId);
    if (anchor.length) {
      anchor.click()
    } else {
      modal.foundation('reveal', 'open');
    }
  }

  $(document).on('opened.fndtn.reveal', '[data-reveal]', function () {
    var modal = $(this),
        video = $('[data-video-id]', modal);
    if (video.length && typeof OO !== 'undefined') {
      var width = $('body').hasClass('ie8') ? '460px' : '100%',
          player = OO.Player.create(video.attr('id'), video.data('video-id'), {width: width, height: '260px'});
      modal.data('ooyala_player', player);
    }
  });

  // Placeholder fix
  $(document).on('focus', '.placeholdersjs', function(){
    $(this).addClass('focused_placeholder');
  }).on('blur', '.placeholdersjs', function(){
    $(this).removeClass('focused_placeholder');
  });

  $.xblock.getRuntime().listenTo('navigation', function(event, data) {
    var mapping = {'lock': 'addClass', 'unlock': 'removeClass'};
    var result = mapping[data.state];
    if (result !== undefined) {
      var arrows = $('.page-to');
      arrows[result]('disabled');
    }
  })
});
