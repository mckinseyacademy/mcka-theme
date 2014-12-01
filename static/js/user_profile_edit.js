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
    ImageFileName = $(this).val();
    if(ImageFileName.length > 27){
      ImageFileName = (ImageFileName.split('\\').pop().substring(0, 27) + "...");
    }
    $('label[for="id_profile_image"]').text(ImageFileName);
    imageEditor.DoFileUpload(e, $(this), imageClass, modal);
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

