massParticipantsEnrollInit = function(){

  if($('#id_student_enroll_list').parents('#enroll_to_course_from_csv').length > 0) {
    $(document).on('open.fndtn.reveal', '[data-reveal]', function () {
      setTimeout(function(){
        var element = $('#id_student_enroll_list');
        var form = element.parents('form')
        element.val('');
        form.find('#enroll_to_course_from_csv input[type=submit]').attr('disabled', 'disabled');
        form.find('#attempted-enroll').val('0');
        form.find('#succeded-enroll').val('0');
        form.find('#failed-enroll').val('0');
        form.find('#enroll-participants-error-list').empty();
        $(document).trigger('clearDropzone');
      }, 10);
    });

    Dropzone.options.participantsEnrollCsvUpload = {
      paramName: 'student_enroll_list',
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
          var form = $('#enroll_to_course_from_csv #participantsEnrollCsvUpload');
          checkForEnrollStatus(response, form);
        });
        _this.on("addedfile", function(file) { 
          $('#enroll_to_course_from_csv .upload_stats').empty();
          $('#enroll-participants-error-list').empty();
          $('#enroll_to_course_from_csv input[type=submit]').removeAttr('disabled');
        });
        _this.on("removedfile", function(file) { 
          if (document.getElementById("id_student_enroll_list").files.length == 0) {
            $('#enroll_to_course_from_csv input[type=submit]').attr('disabled', 'disabled');
          }
          $('#enroll_to_course_from_csv .upload_stats').empty();
          $('#enroll-participants-error-list').empty();
        });
      }
    };
  }

  $('#id_student_enroll_list, .select-program, .select-course').on("change", function(){
    var program = $('#enroll_to_course_from_csv .select-program').find(":selected").val();
    var course = $('#enroll_to_course_from_csv .select-course').find(":selected").val();
    if(program != 'select' && course != 'select' && $('#id_student_enroll_list').val() != '') {
      $('#enroll_to_course_from_csv input[type=submit]').removeAttr('disabled');
    }
  });

  $('#id_student_enroll_list').on("change", function(){
    $('#enroll_to_course_from_csv .upload_stats').empty();
    $('#enroll_to_course_from_csv #enroll-participants-error-list').empty();
  });

  $('#enroll_to_course_from_csv .admin-form form').on('click', 'input[type=submit]', function(e){
    e.preventDefault();
    var form = $(this).parents('form');
    var modal = form.parent();
    modal.find('.error').html('');
    $(this).attr('disabled', 'disabled');

    if (document.getElementById("id_student_enroll_list").files.length > 0){
      var options = {
      url     : form.attr('action'),
      type    : 'POST',
      contentType: false,
      processData: false,
      dataType: 'text',
      cache: false,
      success:function( data ) {
        checkForEnrollStatus(data, form);
      },
      error: function( data ){
            data = $.parseJSON(data);
            modal.find('.error').append('<p class="warning">Please select file first.</p>');
            $('#enroll_to_course_from_csv input[type=submit]').removeAttr('disabled');
          }
      }
      form.ajaxSubmit(options);
    }
    else if (modal.find('.dropzone')){
      $(document).trigger('submitDropzone');
    }
  });
}


checkForEnrollStatus = function(data, form) {
  var errorsBlockTemplate =
  "<div class='message'><%= data %>" +
    "<div id='user-enroll-reg-errors' class='errors'></div></div>";

  var errorsTemplate =
    "<a href='#' data-reveal-id='upload_enroll_error_list'>Show Errors</a>" +
    "<ul id='upload_enroll_error_list' class='reveal-modal' data-reveal='true'>" +
      "<div class='close-reveal-modal'>" +
        "<i class='fa fa-times-circle'></i>" +
      "</div>" +
      "<% _.each(data.error, function(errorObj, key){ %>" +
        "<li><%= errorObj.fields.error %></li>" +
      "<% }) %>" +
    "</ul>";

  var errorsTemplateNotModal =
    "<br/>" +
    "<p>Errors:</p>" +
    "<ul id='upload_enroll_error_list'>" +
      "<% _.each(data.error, function(errorObj, key){ %>" +
        "<li><%= errorObj.fields.error %></li>" +
      "<% }) %>" +
    "</ul>";

  var uploadStatsTemplate =
    "<br/>" +
    "<span>Total:</span>" +
    "<span id='attempted-enroll'><%= data.attempted %></span><br/>" +
    "<span>Succeded:</span>" +
    "<span id='succeded-enroll'><%= data.succeded %></span><br/>" +
    "<span>Failed:</span>" +
    "<span id='failed-enroll'><%= data.failed %></span><br/>" +
    "<br/>";

  data = $.parseJSON(data);
  var task_key = data.task_key;
  var poolingInterval = setInterval(function(){
    var url = form.attr('action') + '/check/' + data.task_key;
    $.ajax({
      url: url,
      method: 'GET',
      dataType: 'json',
      processData: false,
      cache: false,
      beforeSend: function( xhr ) {
        xhr.setRequestHeader("X-CSRFToken", $.cookie('apros_csrftoken'));
      }
    }).done(function(data){
      if(data.done === 'done'){
        clearInterval(poolingInterval);
        $('#enroll_to_course_from_csv input[type=submit]').removeAttr('disabled');
        if ($('#participantsEnrollCsvUpload').length) {
          $('#enroll_to_course_from_csv .upload_stats').html(_.template(uploadStatsTemplate, {'data': data}));
        }
        $('#enroll-participants-error-list').html(_.template(errorsBlockTemplate, {'data': data.message}));
        if(data.error.length > 0){
          if ($('#participantsEnrollCsvUpload').length) {
            $('#attempted-enroll').text(data.attempted);
            $('#succeded-enroll').text(data.succeded);
            $('#failed-enroll').text(data.failed);
            $('#enroll-participants-error-list').find('#user-enroll-reg-errors').html(_.template(errorsTemplateNotModal, {'data': data}));
          }
        }
      }
      else if(data.done === 'failed-enroll'){
        clearInterval(poolingInterval);
        $('#enroll_to_course_from_csv input[type=submit]').removeAttr('disabled');
      }
      else if(data.done === 'progress'){
        if ($('#participantsEnrollCsvUpload').length) {
          $('#enroll_to_course_from_csv .upload_stats').html(_.template(uploadStatsTemplate, {'data': data}));
        }
      }
      else{
      }
    })
  }, 10000);
}