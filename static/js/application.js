$(function(){
  /* Javascript to initialise on ready as defined by jquery */

  // Load user profile information on demand
  $('.user-info').one('click', function(){
    if($('#profile-container .user-profile').length < 1){
      $('body, .user-info').css('cursor', 'wait');
      $('#profile-container').load('/users/user_profile.html', function(){
        $('body, .user-info').css('cursor', 'inherit');
      });
    }
  });

  $('#profile-container').on('closed opened', function(){
    $('.user-info >.fa').toggleClass('fa-sort-asc fa-sort-desc');
  })
}
);
