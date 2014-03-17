$(function(){
  /* Javascript to initialise on ready as defined by jquery */

  // Toggle user profile information
  $('.user-info >.user-name, .user-info >.user-image').on('click', function(){
    var $profile = $('#profile-container');
    var $user_profile = $profile.find('.user-profile');
    if($user_profile.length < 1){
      $profile.load('/users/user_profile.html')
    }
    else{
      $user_profile.toggle();
    }
    $('.user-info >.fa').toggleClass('fa-sort-asc, fa-sort-desc');
  });
}
);
