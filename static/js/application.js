$(function(){
  /* Javascript to initialise on ready as defined by jquery */
  $('#login').on('click', function(){
    location.href = './login'
  });

  $('.user-info >.user-name, .user-info >.user-image').on('click', function(){
    var $profile = $('#profile-container');
    var $user_profile = $profile.find('.user-profile');
    if($user_profile.length < 1){
      $profile.load('/users/user_profile.html')
    }
    else{
      $user_profile.toggle();
    }
  });
}
);
