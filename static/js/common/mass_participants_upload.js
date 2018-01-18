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
        checkForStatus(data, form);
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


checkForStatus = function(data, form) {

  var errorsBlockTemplate =
  "<div class='message'><%= data %>" +
    "<div id='user-reg-errors' class='errors'></div></div>";

  var errorsTemplate =
    "<a href='#' data-reveal-id='upload_error_list'>"+gettext('Show Errors')+"</a>" +
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
    "<p>"+gettext('Errors:')+"</p>" +
    "<ul id='upload_error_list'>" +
      "<% _.each(data.error, function(errorObj, key){ %>" +
        "<li><%= errorObj.fields.error %></li>" +
      "<% }) %>" +
    "</ul>";

  var uploadStatsTemplate =
    "<br/>" +
    "<span>"+gettext('Total:')+"</span>" +
    "<span id='attempted'>"+gettext('0')+"</span><br/>" +
    "<span>"+gettext('Succeded:')+"</span>" +
    "<span id='succeded'>"+gettext('0')+"</span><br/>" +
    "<span>"+gettext('Failed:')+"</span>" +
    "<span id='failed'>"+gettext('0')+"</span><br/>" +
    "<br/>";

  data = $.parseJSON(data);
  var task_key = data.task_key;
  var poolingInterval = setInterval(function(){
    var url = form.attr('action') + '/check/' + data.task_key;
    if ($('#participantsCsvUpload').length) {
      var emails = $('#import_from_csv .emailActivationLinkCheckboxWrapper').find('input').is(":checked");
      url = url + '?emails=' + emails;
    }
    $.ajax({
      url: url,
      method: 'GET',
      dataType: 'json',
      processData: false,
      cache: false,
      'csrfmiddlewaretoken': form.find('[name="csrfmiddlewaretoken"]').val()
    }).done(function(data){
      if(data.done == 'done'){
        clearInterval(poolingInterval);
        $('#import_from_csv input[type=checkbox]').removeAttr('disabled');
        $('input[type=submit]').removeAttr('disabled');
        if ($('#participantsCsvUpload').length) {
          $('.upload_stats').html(_.template(uploadStatsTemplate, {'data': data}));
        }
        $('#enroll-error-list').html(_.template(errorsBlockTemplate, {'data': data.message}));
        if(data.error.length > 0){
          if ($('#participantsCsvUpload').length) {
            $('#attempted').text(data.attempted);
            $('#succeded').text(data.succeded);
            $('#failed').text(data.failed);
            $('#enroll-error-list').find('#user-reg-errors').html(_.template(errorsTemplateNotModal, {'data': data}));
          }
          else {
            $('#enroll-error-list').find('#user-reg-errors').html(_.template(errorsTemplate, {'data': data}));
            $("#upload_error_list").foundation('reveal');
          }
        }
        else {
          if (data.emails == 'true') {
            $("#confirmation_screen .downloadActivationLinksConfirmationScreen" ).hide();
            $('#confirmation_screen .upload_message').text(data.message);
            $("#confirmation_screen .sendActivationLinksConfirmationScreen" ).show();
          }
          else {
            $("#confirmation_screen .sendActivationLinksConfirmationScreen" ).hide();
            $('#confirmation_screen .upload_message').text(data.message);
            $('#confirmation_screen .download_activation').attr('href', $('.download_activation').attr('href') + task_key);
            $("#confirmation_screen .downloadActivationLinksConfirmationScreen" ).show();
          }
          $('#confirmation_screen').foundation('reveal', 'open');
        }
      }
      else if(data.done == 'failed'){
        clearInterval(poolingInterval);
        $('#import_from_csv input[type=checkbox]').removeAttr('disabled');
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