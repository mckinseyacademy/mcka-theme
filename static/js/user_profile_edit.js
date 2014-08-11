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

    $('#edit-user-image-modal').fileupload({
        dataType: 'html',
        autoUpload: true,
        replaceFileInput: false,
        change: function(e, data){
          modal = $('#edit-user-image-modal');
          modal.find('.error').html('');
        },
        send: function(e, data){
          if(data.fileInput.length > 0){
            return FileTypeValidate(data.fileInput[0].value, modal.find('.error'));
          }
          return false;
        },
        done: function (e, data) {
          if(data.textStatus == 'success'){
            $('#edit-user-image-modal').fileupload('destroy');
            modal.html(data.result);
            reloadImages();
          }
        },
        fail: function(e, data) {
          modal.find('.error').append('<p class="warning">Please select file first.</p>');
        },
        progress: function (e, data) {
        var progress = parseInt(data.loaded / data.total * 100, 10);
        $('#progress .bar').css(
            'width',
            progress + '%'
        );
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


  function FileTypeValidate(fileUpload, errorBlock) {

      var extension = fileUpload.substring(fileUpload.lastIndexOf('.'));
      var ValidFileType = ".jpg , .png , .gif";

      //check whether user has selected file or not
      if (fileUpload.length > 0) {

          //check file is of valid type or not
          if (ValidFileType.toLowerCase().indexOf(extension) < 0) {
              errorBlock.html("Please select valid file type.");
          }
          else{
            return true;
          }
      }
      else {
          errorBlock.html("Please select file for upload.");
      }
      return false;
  }

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
    var modal = $('#edit-user-image-modal');
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
})
