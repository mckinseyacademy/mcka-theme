$.imageEditor = function(){

  var ImageFileName = "No file Selected";
  var aspectRatio = 1;

  function reInitCropper(imageClass, modal){
    var $image = modal.find(".img-container").find(imageClass),
    $dataX1 = modal.find(".x1-position"),
    $dataY1 = modal.find(".y1-position"),
    $dataHeight = modal.find(".height-position"),
    $dataWidth = modal.find(".width-position");
    $image.cropper({
      aspectRatio: aspectRatio,
      crop: function(e) {
        $dataX1.val(e.x);
        $dataY1.val(e.y);
        $dataHeight.val(e.height);
        $dataWidth.val(e.width);      }
    });
  }

  function reloadImages(imageClass, modal, AR){
    var d = new Date();
    var now = d.getTime();
    if (typeof AR != 'undefined'){
      aspectRatio = AR;
    }
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

  function applyCropperToImage(that, imageClass, modal) {
    var validate = FileTypeValidate(that.val(), modal.find('.error'));
    ImageFileName = that.val().replace(/^.*\\/, "").length > 25 ? (that.val().replace(/^.*\\/, "").substr(0,25) + '...') : that.val().replace(/^.*\\/, "");

    $('label[for="'+that.attr('id')+'"]').text(ImageFileName);
    reloadImages(imageClass, modal, aspectRatio);
  }

  function previewSelectedImage(input, preview_image_class) {
    $(preview_image_class).cropper('destroy');
    if (input.files && input.files[0]) {
      var reader = new FileReader();

      reader.onload = function (e) {
        $(preview_image_class).attr('src', e.target.result);
      }
      reader.readAsDataURL(input.files[0]);
    }
  }


  return {
          reInitCropper : reInitCropper,
          reloadImages: reloadImages,
          applyCropperToImage: applyCropperToImage,
          previewSelectedImage: previewSelectedImage
        }
}
