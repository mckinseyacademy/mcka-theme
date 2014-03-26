$(function(){
  /* Javascript to initialise on ready as defined by jquery */

  var toggle_menu = function(container_selector, menu_selector, menu_content_url, fn_callback){
    var $container = $(container_selector);
    var $pop_up = $container.find(menu_selector);
    if($pop_up.length < 1 && menu_content_url){
      $container.load(menu_content_url);
    }
    else{
      $pop_up.toggle();
    }

    if(fn_callback)
      fn_callback();
  }
  // Toggle user profile information
  $('.user-info >.user-name, .user-info >.user-image').on('click', function(){
    toggle_menu('#profile-container', '.user-profile', '/users/user_profile.html', function(){
      $('.user-info >.fa').toggleClass('fa-sort-asc fa-sort-desc');
    });
  });

  // Toggle course navigation menu
  $('.program-menu >.fa').on('click', function(){
    toggle_menu('.program-menu', '.program-menu-content');
  });

}
);
