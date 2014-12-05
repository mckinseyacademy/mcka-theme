$(function(){

  var imageClass = ".company-uploaded-image";
  var imageEditor = $.imageEditor();
  var modal = $('#edit-company-image-modal');
  var aspectRatio = 3.5;

  $(document).on('opened.fndtn.reveal', '#edit-company-image-modal', function () {
    $(this).find('img').error(function() {
      $(this).hide();
    });
    imageEditor.reloadImages(imageClass, modal, aspectRatio);
  });

  $(document).on('closed.fndtn.reveal', '#edit-company-image-modal', function () {
    if($('#edit_image_client_id').val() == 'new'){
      $('#new-principal').foundation('reveal', 'open');
    }
    else{
      $('#edit-principal').foundation('reveal', 'open');
    }
  });

  $(document).on('mouseenter', '#id_company_image', function(){
    $('#browse-company-image').addClass('hover');
  });

  $(document).on('mouseleave', '#id_company_image', function(){
    $('#browse-company-image').removeClass('hover');
  });

  $('#edit-company-image-modal').on('click', '#browse-company-image', function(){
    $('label[for="id_company_image"]').trigger('click');
  });

  $('#edit-company-image-modal').on('change', '#id_company_image', function(e){
    ImageFileName = $(this).val();
    if(ImageFileName.length > 27){
      ImageFileName = (ImageFileName.split('\\').pop().substring(0, 27) + "...");
    }
    $('label[for="id_company_image"]').text(ImageFileName);
    imageEditor.DoFileUpload(e, $(this), imageClass, modal);
  });

  $('#edit-company-image-modal').on('submit', '#company-cropping-form', function(e){
    e.preventDefault();
    $('#upload-image-url').val($('.img-container .company-uploaded-image').attr('src'));
    var form = $(this);
    var modal = $('#edit-company-image-modal');
    $.ajax({
      method: 'POST',
      url: form.attr('action'),
      data: form.serialize()
    }).done(function(data){
        if(typeof(data) != 'undefined'){
          if(typeof data.image_url != 'undefined' && typeof data.client_id == 'undefined'){
              $('#new-principal').foundation('reveal', 'open');
              $('.company-image img').attr('src', data.image_url + '?' + new Date().getTime());
              $('#id_logo_url').val(data.image_url);
          }
          else if(typeof data.client_id != 'undefined'){
              $('#edit-principal').foundation('reveal', 'open');
              $('.company-image img').attr('src', data.image_url + '?' + new Date().getTime());
              $('#id_logo_url').val(data.image_url);
          }
          else{
            $('#edit-company-image-modal').foundation('reveal', 'close');
          }
        }
      });
    });
})

