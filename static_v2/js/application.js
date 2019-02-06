
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
              $('#profile-container').addClass("open");
              $("#profileDropdown").addClass("block-view");

              $('.user-profile .logout a').on('click', function(){
                var href = $(this).attr('href');
                if(href.length > 1){
                  window.location.href = href;
                }
              });
            }
          });
    }
    else{
      $("#profileDropdown").toggleClass("block-view");
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
        // Remove user profile container
        $('#profile-container').empty();
      }
    });
  });

  $('#profile-container').on('closed opened', function(){
    $('.user-info >.fa').toggleClass('fa-sort-asc fa-sort-desc');
  });
