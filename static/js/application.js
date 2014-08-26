window.Apros = {
  models: {},
  collections: {},
  views: {},

  initialize: function() {
    var route     = window.location.pathname.replace(/\/$/, ''),
        has_push  = window.history && window.history.pushState ? true : false;
    $('header[role=banner] a[href="' + route + '"]').addClass('selected');
    Backbone.history.start({pushState: has_push, hashChange: false});
  }
}

_(Apros).extend(Backbone.Events);

$(function(){
  Apros.initialize()
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
        var ooyala = OO.Player.create('ooyala_mckinsey', video, {width: '100%', height: '100%'});
        modal.data('ooyala', ooyala);

    }
  });

  $(document).on('close', '[data-reveal]', function () {
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
});
