$(document).ready(function(){

  // var $image = $('.user-uploaded-image');

  var current_image = $('.user-uploaded-image').attr('src');
  var $image = $('.user-uploaded-image'),
    $dataX1 = $(".editPhotoModal .x1-position"),
    $dataY1 = $(".editPhotoModal .y1-position"),
    $dataHeight = $(".editPhotoModal .height-position"),
    $dataWidth = $(".editPhotoModal .width-position");
  var cropBoxData;
  var canvasData;

  function applyCropper() {
      $image.cropper({
          aspectRatio: 1,
          ready: function () {
              $image.cropper('setCanvasData', canvasData);
              $image.cropper('setCropBoxData', cropBoxData);
          },
          crop: function(e) {
          $dataX1.val(e.x);
          $dataY1.val(e.y);
          $dataHeight.val(e.height);
          $dataWidth.val(e.width);
          }
      });
  }

  function removeCropper() {
      cropBoxData = $image.cropper('getCropBoxData');
      canvasData = $image.cropper('getCanvasData');
      $image.cropper('destroy');
  }
  
  function applyCoordinates() {
      removeCropper();
      alert(canvasData);
      $(".editPhotoModal .x1-position").val(canvasData.left);
      $(".editPhotoModal .y1-position").val(canvasData.top);
      $(".editPhotoModal .height-position").val(canvasData.height);
      $(".editPhotoModal .width-position").val(canvasData.width);
  }

   $(".browseProfilePhoto").change(function(event) {
        removeCropper();
        $(".user-uploaded-image").attr("src", "");
        $(".user-uploaded-image").attr("src", URL.createObjectURL(event.target.files[0]));
        applyCropper();
   });

  $(".editPhotoModal").on('shown.bs.modal', function () {
      $('.user-uploaded-image').attr('src', current_image);
      applyCropper();
  });

  $(".editPhotoModal").on('hidden.bs.modal', function () {
    removeCropper();
  });

});

