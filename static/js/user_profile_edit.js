$(function(){

  var ImageFileName = "No file Selected";

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

  function FileUploadInit(){
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
            var validate = FileTypeValidate(data.fileInput[0].value, modal.find('.error'));
            if(validate){
              $('img.spinner.upload-profile').show();
            }
            return validate;
          }
          return false;
        },
        done: function (e, data) {
          if(data.textStatus == 'success'){
            $('#edit-user-image-modal').fileupload('destroy');
            modal.html(data.result);
            $('label[for="browse-image"]').text(ImageFileName);
            reloadImages();
          }
        },
        always: function(e, data){
          $('img.spinner.upload-profile').hide();
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
    FileUploadInit();
  }


  function FileTypeValidate(fileUpload, errorBlock) {

      var extension = fileUpload.substring(fileUpload.lastIndexOf('.'));
      var ValidFileType = ".jpg , .png , .gif";

      //check whether user has selected file or not
      if (fileUpload.length > 0) {

          //check file is of valid type or not
          if (ValidFileType.toLowerCase().indexOf(extension) < 0) {
              errorBlock.html("Error uploading file. Please try again and be sure to use an accepted file format.");
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

  $('#edit-user-image-modal').on('click', '#browse-image', function(){
    $('#id_profile_image').trigger('click');
  });

  $('#edit-user-image-modal').on('change', '#id_profile_image', function(e){
    ImageFileName = $(this).val();
    if(ImageFileName.length > 27){
      ImageFileName = (ImageFileName.substring(0, 27) + "...");
    }
    $('label[for="browse-image"]').text(ImageFileName);
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
