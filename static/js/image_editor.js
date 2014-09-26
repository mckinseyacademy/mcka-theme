$.imageEditor = function(){

  var ImageFileName = "No file Selected";

  function reInitCropper(imageClass, modal){
    var $image = modal.find(".img-container").find(imageClass),
    $dataX1 = modal.find(".x1-position"),
    $dataY1 = modal.find(".y1-position"),
    $dataX2 = modal.find(".x2-position"),
    $dataY2 = modal.find(".y2-position"),
    $dataHeight = modal.find(".height-position"),
    $dataWidth = modal.find(".width-position"),
    $profileImageUrl = modal.find(".upload-image-url");
    $image.cropper({
        aspectRatio: 1,
        done: function(data) {
                $dataX1.val(data.x1);
                $dataY1.val(data.y1);
                $dataX2.val(data.x2);
                $dataY2.val(data.y2);
                $dataHeight.val(data.height);
                $dataWidth.val(data.width);
                $profileImageUrl.val($(imageClass).attr('src'));
            }
    });
  }

  function reloadImages(imageClass, modal){
    var d = new Date();
    var now = d.getTime();
    modal.find(".img-container").find(imageClass).load(function(){
      if($(this).attr('src').indexOf('/empty_avatar.png') == -1){
        $('.crop-save-image').attr('disabled', false);
        reInitCropper(imageClass, modal);
      }
    }).attr('src', modal.find(".img-container").find(imageClass).attr('src') + '&' + now);
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

  function DoFileUpload(e, that, imageClass, modal){
      var form = that.parents('form').first();
      modal.find('.error').html('');
      var validate = FileTypeValidate(that.val(), modal.find('.error'));
      if(validate){
        $('img.spinner.upload-image').show();
        var options = {
                    url     : form.attr('action'),
                    type    : 'POST',
                    contentType: false,
                    success:function( data ) {
                        $('img.spinner.upload-image').hide();
                          modal.html(data);
                          $('label[for="id_profile_image"]').text(ImageFileName);
                          reloadImages(imageClass, modal);
                        },
                    error: function( data ){
                          $('img.spinner.upload-image').hide();
                          modal.find('.error').append('<p class="warning">Please select file first.</p>');
                        }
                    }

      form.ajaxSubmit(options);
    }
  }

  return {
          reInitCropper : reInitCropper,
          reloadImages: reloadImages,
          DoFileUpload: DoFileUpload
        }
}
