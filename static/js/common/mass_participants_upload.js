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
          checkForStatus(response, form);
        });
        _this.on("addedfile", function(file) { 
          $('input[type=submit]').removeAttr('disabled');
        });
        _this.on("removedfile", function(file) { 
          if (document.getElementById("id_student_list").files.length == 0) {
            $('input[type=submit]').attr('disabled', 'disabled');
          }
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

  $('.admin-form form').on('click', 'input[type=submit]', function(e){
    e.preventDefault();
    var form = $(this).parents('form');
    var modal = form.parent();
    modal.find('.error').html('');
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
        checkForStatus(data, form);
      },
      error: function( data ){
            data = $.parseJSON(data);
            modal.find('.error').append('<p class="warning">Please select file first.</p>');
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


checkForStatus = function(data, form) {

  var errorsBlockTemplate =
  "<div class='message'><%= data %>" +
    "<div id='user-reg-errors' class='errors'></div></div>";

  var errorsTemplate =
    "<a href='#' data-reveal-id='upload_error_list'>Show Errors</a>" +
    "<ul id='upload_error_list' class='reveal-modal' data-reveal='true'>" +
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
    "<ul id='upload_error_list'>" +
      "<% _.each(data.error, function(errorObj, key){ %>" +
        "<li><%= errorObj.fields.error %></li>" +
      "<% }) %>" +
    "</ul>";

  var uploadStatsTemplate =
    "<hr/>" +
    "<span>Total:</span>" +
    "<span id='attempted'>0</span><br/>" +
    "<span>Succeded:</span>" +
    "<span id='succeded'>0</span><br/>" +
    "<span>Failed:</span>" +
    "<span id='failed'>0</span><br/>" +
    "<br/>";

  data = $.parseJSON(data);
  var task_key = data.task_key;
  var poolingInterval = setInterval(function(){
    $.ajax({
      url: form.attr('action') + '/check/' + data.task_key,
      method: 'GET',
      dataType: 'json',
      processData: false,
      cache: false,
      'csrfmiddlewaretoken': form.find('[name="csrfmiddlewaretoken"]').val()
    }).done(function(data){
      if(data.done == 'done'){
        clearInterval(poolingInterval);
        $('input[type=submit]').removeAttr('disabled');
        if ($('#participantsCsvUpload').length) {
          $('.upload_stats').html(_.template(uploadStatsTemplate));
        }
        $('#enroll-error-list').html(_.template(errorsBlockTemplate, {'data': data.message}));
        if(data.error.length > 0){
          if ($('#participantsCsvUpload').length) {
            $('#enroll-error-list').find('#user-reg-errors').html(_.template(errorsTemplateNotModal, {'data': data}));
          }
          else {
            $('#enroll-error-list').find('#user-reg-errors').html(_.template(errorsTemplate, {'data': data}));
            $("#upload_error_list").foundation('reveal');
          }
        }
        else {
          $('#confirmation_screen').foundation('reveal', 'open');
          $('.upload_message').text(data.message);
          $('.download_activation').attr('href', $('.download_activation').attr('href') + task_key);
        }
      }
      else if(data.done == 'failed'){
        clearInterval(poolingInterval);
        $('input[type=submit]').removeAttr('disabled');
      }
      else{
        $('#attempted').text(data.attempted);
        $('#succeded').text(data.succeded);
        $('#failed').text(data.failed);
      }
    })
  }, 10000);
}