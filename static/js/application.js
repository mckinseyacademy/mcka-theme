window.Apros = {
  models: {},
  collections: {},
  views: {},

  initialize: function() {
    Backbone.history.start({pushState: true});
  }
}

_(Apros).extend(Backbone.Events);

$(function(){
  Apros.initialize()
  /* Javascript to initialise on ready as defined by jquery */

  // Load user profile information on demand
  $('.user-info').one('click', function(){
    if($('#profile-container .user-profile').length < 1){
      $('body, .user-info').css('cursor', 'wait');
      $('#profile-container').load('/accounts/user_profile.html', function(){
        $('body, .user-info').css('cursor', 'inherit');

        // Need this, for some reason, the anchor links are not hooked up properly... perhaps investigate more later
        $('.user-profile a').on('click', function(){
          var href = $(this).attr('href');
          if(href.length > 1){
            window.location.href = href;
          }
        });
      });
    }
  });

  $('#profile-container').on('closed opened', function(){
    $('.user-info >.fa').toggleClass('fa-sort-asc fa-sort-desc');
  });

});
