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
        modal.html(data);
        reInitCropper();
      });
    });

    $('#edit-user-image-modal').on('submit', '#upload-profile-image-form', function(e){
    e.preventDefault();
    var form = $(this);
    var formData = new FormData(form[0]);
    var modal = form.parent();
    $.ajax({
      method: 'POST',
      url: form.attr('action'),
      data: formData,
      processData: false,
      contentType: false
    }).done(function(data){
        modal.html(data);
        reInitCropper();
      });
    });
})
