$(function(){

  var imageClass = ".user-uploaded-image";
  var imageEditor = $.imageEditor();
  var modal = $('#edit-user-image-modal');
  var aspectRatio = 1;

  $(document).on('opened.fndtn.reveal', '#edit-user-image-modal', function () {
    $(this).find('img').error(function() {
      $(this).hide();
    });
    imageEditor.reloadImages(imageClass, modal, aspectRatio);
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
    imageEditor.previewSelectedImage(e.target, '.user-uploaded-image')
    imageEditor.applyCropperToImage($(this), imageClass, modal);
  });

  $('#edit-user-image-modal').on('submit', '#cropping-form', function(e){
    e.preventDefault();
    var form = $(this);
    var options = {
      url     : form.attr('action'),
      type    : 'POST',
      contentType: false,
      success:function(data) {
        $('#edit-client-mobile-logo-modal').foundation('reveal', 'close');
      }
    }

    form.ajaxSubmit(options);
  });
})

