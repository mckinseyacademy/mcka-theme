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
          if (ValidFileType.toLowerCase().indexOf(extension.toLowerCase()) < 0) {
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

  function DoFileUpload(e, that){
      var form = that.parents('form').first();
      var modal = $('#edit-user-image-modal');
      modal.find('.error').html('');
      var validate = FileTypeValidate(that.val(), modal.find('.error'));
      if(validate){
        $('img.spinner.upload-profile').show();
        var options = {
                    url     : form.attr('action'),
                    type    : 'POST',
                    contentType: false,
                    success:function( data ) {
                        $('img.spinner.upload-profile').hide();
                          modal.html(data);
                          $('label[for="id_profile_image"]').text(ImageFileName);
                          reloadImages();
                        },
                    error: function( data ){
                          $('img.spinner.upload-profile').hide();
                          modal.find('.error').append('<p class="warning">Please select file first.</p>');
                        }
                    }

      form.ajaxSubmit(options);
    }
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

  $(document).on('mouseenter', '#id_profile_image', function(){
    $('#browse-image').addClass('hover');
  });

  $(document).on('mouseleave', '#id_profile_image', function(){
    $('#browse-image').removeClass('hover');
  });

  $('#edit-user-image-modal').on('click', '#browse-image', function(){
    $('label[for="id_profile_image"]').trigger('click');
  });

  $('#edit-user-image-modal').on('change', '#id_profile_image', function(e){
    ImageFileName = $(this).val();
    if(ImageFileName.length > 27){
      ImageFileName = (ImageFileName.split('\\').pop().substring(0, 27) + "...");
    }
    $('label[for="id_profile_image"]').text(ImageFileName);
    DoFileUpload(e, $(this));
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

