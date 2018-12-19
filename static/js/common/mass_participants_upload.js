massParticipantsInit = function(){

  if($('#id_student_list').parents('#import_from_csv').length > 0) {
    $(document).on('open.fndtn.reveal', '[data-reveal]', function () {
      setTimeout(function(){
        var element = $('#id_student_list');
        var form = element.parents('form')
        element.val('');
        form.find('input[type=submit]').attr('disabled', 'disabled');
        form.find('#attempted').val('0');
        form.find('#succeded').val('0');
        form.find('#failed').val('0');
        form.find('#enroll-error-list').empty();
        $(document).trigger('clearDropzone');
      }, 10);
    });

    Dropzone.options.participantsCsvUpload = {
      paramName: 'student_list',
      headers: { 'X-CSRFToken': $.cookie('apros_csrftoken')},
      autoProcessQueue: false,
      addRemoveLinks: true,
      init: function() {
        var _this = this;
        $(document).on('submitDropzone', function() {
          var fileList = _this.getQueuedFiles().length;
          if (fileList > 0){
            _this.processQueue();
          }
        });
        $(document).on('clearDropzone', function() {
          _this.removeAllFiles(true);
        });
        _this.on('success', function(file, response) {
          var form = $('#participantsCsvUpload');
          $('#import_participants_popup_message').foundation('reveal', 'open');
        });
        _this.on("addedfile", function(file) { 
          $('.upload_stats').empty();
          $('#enroll-error-list').empty();
          $('#import_from_csv input[type=checkbox]').removeAttr('disabled');
          $('input[type=submit]').removeAttr('disabled');
        });
        _this.on("removedfile", function(file) { 
          if (document.getElementById("id_student_list").files.length == 0) {
            $('input[type=submit]').attr('disabled', 'disabled');
            $('#import_from_csv input[type=checkbox]').attr('checked', false);
            $('#import_from_csv input[type=checkbox]').attr('disabled', 'disabled');
          }
          $('.upload_stats').empty();
          $('#enroll-error-list').empty();
        });
      }
    };
  }

  $('#id_student_list, .select-program, .select-course').on("change", function(){
    var program = $('.select-program').find(":selected").val();
    var course = $('.select-course').find(":selected").val();
    if(program != 'select' && course != 'select' && $('#id_student_list').val() != '') {
      $('input[type=submit]').removeAttr('disabled');
    }
  });

  $('#id_student_list').on("change", function(){
    $('.upload_stats').empty();
    $('#enroll-error-list').empty();
    if (document.getElementById("id_student_list").files.length > 0) {
      $('#import_from_csv input[type=checkbox]').removeAttr('disabled');
    }
  });

  $('.admin-form form').on('click', 'input[type=submit]', function(e){
    e.preventDefault();
    var form = $(this).parents('form');
    var modal = form.parent();
    modal.find('.error').html('');
    $('#import_from_csv input[type=checkbox]').attr('disabled', 'disabled');
    $(this).attr('disabled', 'disabled');

    if (document.getElementById("id_student_list").files.length > 0){
      var options = {
      url     : form.attr('action'),
      type    : 'POST',
      contentType: false,
      processData: false,
      dataType: 'text',
      cache: false,
      success:function( data ) {
        $('#import_participants_popup_message').foundation('reveal', 'open');
      },
      error: function( data ){
            data = $.parseJSON(data);
            modal.find('.error').append('<p class="warning">'+gettext("Please select file first.")+'</p>');
            $('#import_from_csv input[type=checkbox]').removeAttr('disabled');
            $('input[type=submit]').removeAttr('disabled');
          }
      }
      form.ajaxSubmit(options);
    }
    else if (modal.find('.dropzone')){
      $(document).trigger('submitDropzone');
    }
  });
}
