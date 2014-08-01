$(function(){

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
                $profileImageUrl.val($('img.user-uploaded-image').attr('src'));
            }
    });
  }

  function reloadImages(){
    var d = new Date();
    var now = d.getTime();
    $(".img-container .user-uploaded-image").load(function(){
      if($(this).attr('src').indexOf('/empty_avatar.png') == -1){
        $('#crop-profile-image').attr('disabled', false);
        reInitCropper();
      }
    }).attr('src', $(".img-container .user-uploaded-image").attr('src') + '&' + now);
  }

  $('#edit-user-image-modal').on("change", '#id_profile_image', function(){
    $('input[type=submit]').attr('disabled', false);
  });

  $(document).on('opened.fndtn.reveal', '#edit-user-image-modal', function () {
    $(this).find('img').error(function() {
      $(this).hide();
    });
    reloadImages();
  });

  $(document).on('closed.fndtn.reveal', '#edit-user-image-modal', function () {
    window.location.reload(true);
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
        if(data){
          $('#edit-user-image-modal').foundation('reveal', 'close');
        }
      });
    });

    $('#edit-user-image-modal').on('click', '#user-image-submit', function(e){
      e.preventDefault();
      var form = $(this).parent('form');
      var modal = form.parent();
      modal.find('.error').html('');

      var options = {
                  url     : form.attr('action'),
                  type    : 'POST',
                  contentType: false,
                  success:function( data ) {
                        modal.html(data);
                        reloadImages();
                      },
                  error: function( data ){
                        modal.find('.error').append('<p class="warning">Please select file first.</p>');
                      }
                  }

    form.ajaxSubmit(options);
    });
})
