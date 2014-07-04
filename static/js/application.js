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
      $('#profile-container').load('/accounts/user_profile.html', function(){
        $('body, .user-info').css('cursor', 'inherit');

        // Need this, for some reason, the anchor links are not hooked up properly... perhaps investigate more later
        $('.user-profile .logout a').on('click', function(){
          var href = $(this).attr('href');
          if(href.length > 1){
            window.location.href = href;
          }
        });

        var modals = $(
          '<div data-reveal id="edit_fullname_modal" class="reveal-modal small"></div>' +
          '<div data-reveal id="edit_title_modal" class="reveal-modal small"></div>');
        $(document.body).append(modals);
    /*    $(document).foundation({bindings: 'events'}); */

        modals.on('submit', 'form', function(e) {
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

      });
    }
  });

  $('#profile-container').on('closed opened', function(){
    $('.user-info >.fa').toggleClass('fa-sort-asc fa-sort-desc');
  });

  function reInitCropper(){
    var $image = $(".img-container .user-uploaded-image"),
    $dataX1 = $("#x1-position"),
    $dataY1 = $("#y1-position"),
    $dataX2 = $("#x2-position"),
    $dataY2 = $("#y2-position"),
    $dataHeight = $("#height-position"),
    $dataWidth = $("#width-position"),
    $profileImageUrl = $("#profile-image-url");

    $image.cropper({
        aspectRatio: 1,
        done: function(data) {
                $dataX1.val(data.x1);
                $dataY1.val(data.y1);
                $dataX2.val(data.x2);
                $dataY2.val(data.y2);
                $dataHeight.val(data.height);
                $dataWidth.val(data.width);
                $profileImageUrl.val($('img.user-uploaded-image').attr('src').split('?')[0]);
            }
    });
  }

  $('#edit-user-image-modal').on("change", '#id_profile_image', function(){
    $('input[type=submit]').attr('disabled', false);
  });

  $(document).on('opened.fndtn.reveal', '#edit-user-image-modal', function () {
    reInitCropper();
  });

  $('#edit-user-image-modal').on('submit', '#cropping-form', function(e){
    e.preventDefault();
    var form = $(this);
    var modal = form.parent();
    $.ajax({
      method: 'POST',
      url: form.attr('action'),
      data: form.serialize()
    }).done(function(data){
        modal.html(data);
        reInitCropper();
      });
    });
});
