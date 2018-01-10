$(function(){

  var imageClass = ".user-uploaded-image";
  var imageEditor = $.imageEditor();
  var image_type = $('#id_mobile_app_img').attr('name');
  var aspectRatio = 5;
  if(image_type === 'mobile_app_logo')
  {
    aspectRatio = 4.5
  }
  var modal = $('#edit-client-mobile-logo-modal');
  $(document).on('opened.fndtn.reveal', '#edit-client-mobile-logo-modal', function () {
    $(this).find('img').error(function() {
      $(this).hide();
    });
    imageEditor.reloadImages(imageClass, modal, aspectRatio);
  });

  $(document).on('closed.fndtn.reveal', '#edit-client-mobile-logo-modal', function () {
    window.location.reload(true);
  });

  $(document).on('mouseenter', '#id_mobile_app_img', function(){
    $('#browse-image').addClass('hover');
  });

  $(document).on('mouseleave', '#id_mobile_app_img', function(){
    $('#browse-image').removeClass('hover');
  });

  $('#edit-client-mobile-logo-modal').on('click', '#browse-image', function(){
    $('label[for="id_mobile_app_img"]').trigger('click');
  });

  $('#edit-client-mobile-logo-modal').on('change', '#id_mobile_app_img', function(e){
    imageEditor.previewSelectedImage(e.target, '.user-uploaded-image')
    imageEditor.applyCropperToImage($(this), imageClass, modal);
  });

  $('#edit-client-mobile-logo-modal').on('submit', '#cropping-form', function(e){
    e.preventDefault();
    var form = $(this);
    var options = {
      url     : form.attr('action'),
      type    : 'POST',
      contentType: false,
      success: function(data) {
        $('#edit-client-mobile-logo-modal').foundation('reveal', 'close');
      }
    }

    form.ajaxSubmit(options);
  });
})

