massParticipantsEnrollInit = function(){

  if($('#id_student_enroll_list').parents('#enroll_to_course_from_csv').length > 0) {
    $(document).on('open.fndtn.reveal', '[data-reveal]', function () {
      setTimeout(function(){
        var element = $('#id_student_enroll_list');
        var form = $('#enroll_to_course_from_csv');
        element.val('');
        form.find('#submitCSVEnroll').attr('disabled', 'disabled');
        form.find('.button-wrapper i').hide();
        form.find('#id_student_enroll_list').attr('accept', '.csv');
        form.find('#attempted-enroll').val('0');
        form.find('#succeded-enroll').val('0');
        form.find('#failed-enroll').val('0');
        form.find('#enroll-participants-error-list').empty();
        form.find(".upload_stats").empty();
        PopulateTemplateData();
        $(document).trigger('clearDropzone');
      }, 10);
    });

    Dropzone.options.participantsEnrollCsvUpload = {
      paramName: 'student_enroll_list',
      headers: { 'X-CSRFToken': $.cookie('apros_csrftoken')},
      autoProcessQueue: false,
      addRemoveLinks: true,
      acceptedFiles: ".csv",
      maxFilesize: 10,
      init: function() {
        var _this = this;
        $(document).on('submitDropzone', function() {
          var fileList = _this.getQueuedFiles();
          var checked_files = 0;
          var permission = true;
          if (fileList.length > 0){
            var interval_id = setInterval(function()
            {
              if (fileList.length === checked_files){
                if (permission){
                  _this.processQueue();
                }
                clearInterval(interval_id);
              }
            }, 1000);

            for(var i=0; i<fileList.length; i++){
              var reader = new FileReader();
              reader.onload = function(e) {
                var limit = 5000;
                var contents = e.target.result.split(/\n/g);
                var lines = contents.length-1;
                if (contents[lines]=="")
                  lines--;

                if (lines>limit){
                  alert("The .csv file has more then "+limit+ " rows: "+lines+", please split it to more files!");
                  $('#enroll_to_course_from_csv .admin-form').find('.button-wrapper i').hide();
                  $('#enroll_to_course_from_csv #submitCSVEnroll').removeAttr('disabled');
                  permission = permission & false;
                }
                checked_files+=1;
              };
              reader.readAsText(fileList[i]);
            }
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

  $('#enroll_to_course_from_csv .admin-form').on('click', '#submitCSVEnroll', function(e){
    e.preventDefault();
    var ready = false;
    var form = $(this).parents('.admin-form').find(".fileInputEnroll");
    var modal = form.parent();
    modal.find('.error').html('');
    $(this).attr('disabled', 'disabled');
    var _this = this;
    modal.find('.button-wrapper i').show();
    var file_input = document.getElementById("id_student_enroll_list").files;
    if (file_input.length > 0){
      var reader = new FileReader();
      reader.onload = function(e) {
        var limit = 5000
        var contents = e.target.result.split(/\n/g);
        var lines = contents.length-1;
        if (contents[lines]=="")
          lines--;
        var val_result = true;
        if (lines>limit){
          alert("The .csv file has more then "+limit+ " rows: "+lines+", please split it to more files!");
          modal.find('.button-wrapper i').hide();
          $(_this).removeAttr('disabled');
          return;
        }

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
      };
      reader.readAsText(file_input[0]);
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
        $('#enroll_to_course_from_csv .button-wrapper i').hide();
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

PopulateTemplateData = function()
{
  var data = [["email", "course id", "status"], 
  ["sinatest@yopmail.com", "edX/TwoX/Two_Course", "active"], 
  ["sinatest1@yopmail.com", "edX/TwoX/Two_Course", "ta"], 
  ["sinatest2@yopmail.com", "edX/TwoX/Two_Course", "observer"]];
  var csvContent = "data:text/csv;charset=utf-8,";
  data.forEach(function(infoArray, index){

     dataString = infoArray.join(",");
     csvContent += index < data.length ? dataString+ "\n" : dataString;

  }); 
  var encodedUri = encodeURI(csvContent);
  $('#enroll_to_course_from_csv #enrollParticipantTemplate').attr("href", encodedUri);
}