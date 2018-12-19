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
                  var values = {'limit': limit, 'lines': lines};
                  var linesLimitString = gettext("The .csv file has more then %(limit)s  rows: %(lines)s , please split it to more files!");
                  alert(interpolate(linesLimitString, values, true));
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
          $('#import_participants_popup_message').foundation('reveal', 'open');
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
          var values = {'limit': limit, 'lines': lines};
          var linesLimitString = gettext("The .csv file has more then %(limit)s  rows: %(lines)s , please split it to more files!");
          alert(interpolate(linesLimitString, values, true));
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
          $('#import_participants_popup_message').foundation('reveal', 'open');
        },
        error: function( data ){
              data = $.parseJSON(data);
              modal.find('.error').append('<p class="warning">'+gettext('Please select file first.')+'</p>');
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

};

PopulateTemplateData = function()
{
  var data = [[gettext("email"), gettext("course id"), gettext("status")],
  ["sinatest@yopmail.com", "edX/TwoX/Two_Course", "participant"],
  ["sinatest1@yopmail.com", "edX/TwoX/Two_Course", "ta"], 
  ["sinatest2@yopmail.com", "edX/TwoX/Two_Course", "observer"]];
  var csvContent = "data:text/csv;charset=utf-8,";
  data.forEach(function(infoArray, index){

     dataString = infoArray.join(",");
     csvContent += index < data.length ? dataString+ "\n" : dataString;

  }); 
  var encodedUri = encodeURI(csvContent);
  $('#enroll_to_course_from_csv #enrollParticipantTemplate').attr("href", encodedUri);

  var data = [[gettext("Learner email"), gettext("Business Function"), gettext("Business Unit"), gettext('location')],
  ["test@yopmail.com", "abc", "xyz", "New York"],
  ["test1@yopmail.com", "def", "tuv", "Washington"]];
  var csvContent = "data:text/csv;charset=utf-8,";
  data.forEach(function(infoArray, index){

     dataString = infoArray.join(",");
     csvContent += index < data.length ? dataString+ "\n" : dataString;

  });
  var encodedUri = encodeURI(csvContent);
  $('#update_profile_data #companyFieldUpdateDownload').attr("href", encodedUri);

  var data = [[gettext("Learner email"), gettext("Manager email")],
  ["test1@yopmail.com", "abc@yopmail.com"],
  ["test2@yopmail.com", "xyz@yopmail.com"]];
  var csvContent = "data:text/csv;charset=utf-8,";
  data.forEach(function(infoArray, index){

     dataString = infoArray.join(",");
     csvContent += index < data.length ? dataString+ "\n" : dataString;

  });
  var encodedUri = encodeURI(csvContent);
  $('#update_manager_data #managerUpdateDownload').attr("href", encodedUri);

};

massParticipantsProfileUpdateInit = function ()
{
  $('#update_profile_data .admin-form').on('click', '#submitCompanyFieldsUpdate', function(e){
    e.preventDefault();
    var ready = false;
    var form = $(this).parents('.admin-form').find(".fileInputCompanyField");
    var modal = form.parent();
    modal.find('.error').html('');
    $(this).attr('disabled', 'disabled');
    var _this = this;
    modal.find('.button-wrapper i').show();
    var file_input = document.getElementById("id_student_field_list").files;
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
          var values = {'limit': limit, 'lines': lines};
          var linesLimitString = gettext("The .csv file has more then %(limit)s  rows: %(lines)s , please split it to more files!");
          alert(interpolate(linesLimitString, values, true));
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
        success:function(data) {
          data = JSON.parse(data);
          if(data.success) {
            $('i.fa-spinner').hide();
            $('#update_profile_data input[type=submit]').removeAttr('disabled');
            $('#participantUpdateStatus .mainText').html('Report of bulk update will be sent to your email.');
            $('#participantUpdateStatus').foundation('reveal', 'open');
          }
        },
        error: function( data ){
               $('i.fa-spinner').hide();
              data = $.parseJSON(data);
              modal.find('.error').append('<p class="warning">'+gettext('Please select file first.')+'</p>');
              $('#update_profile_data input[type=submit]').removeAttr('disabled');
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

      Dropzone.options.participantsProfileUpdate = {
      paramName: 'student_field_list',
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
                  var values = {'limit': limit, 'lines': lines};
                  var linesLimitString = gettext("The .csv file has more then %(limit)s  rows: %(lines)s , please split it to more files!");
                  alert(interpolate(linesLimitString, values, true));
                  $('#update_profile_data .admin-form').find('.button-wrapper i').hide();
                  $('#update_profile_data #submitCompanyFieldsUpdate').removeAttr('disabled');
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
        _this.on('success', function(file, data) {
            if(data.success) {
              $('i.fa-spinner').hide();
              $('#update_profile_data input[type=submit]').removeAttr('disabled');
              $('#participantUpdateStatus').foundation('reveal', 'open');
              $('#participantUpdateStatus .mainText').html(gettext('Report of bulk update will be sent to your email.'));
            }
        });
        _this.on("addedfile", function(file) {
          $('#update_profile_data .upload_stats').empty();
          $('#update-profile-data-error-list').empty();
          $('#update_profile_data input[type=submit]').removeAttr('disabled');
        });
        _this.on("removedfile", function(file) {
          if (document.getElementById("id_student_field_list").files.length == 0) {
            $('#update_profile_data input[type=submit]').attr('disabled', 'disabled');
          }
        });
      }
    };
};

massParticipantsManagerUpdateInit = function ()
{
  $('#update_manager_data .admin-form').on('click', '#submitManagerUpdate', function(e){
    e.preventDefault();
    var ready = false;
    var form = $(this).parents('.admin-form').find(".fileInputManager");
    var modal = form.parent();
    modal.find('.error').html('');
    $(this).attr('disabled', 'disabled');
    var _this = this;
    modal.find('.button-wrapper i').show();
    var file_input = document.getElementById("id_student_manager_list").files;
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
          var values = {'limit': limit, 'lines': lines};
          var linesLimitString = gettext("The .csv file has more then %(limit)s  rows: %(lines)s , please split it to more files!");
          alert(interpolate(linesLimitString, values, true));
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
        success:function(data) {
          data = JSON.parse(data);
          if(data.success) {
            $('i.fa-spinner').hide();
            $('#update_manager_data input[type=submit]').removeAttr('disabled');
            $('#participantUpdateStatus .mainText').html('Report of bulk update will be sent to your email.');
            $('#participantUpdateStatus .mainText').html('Report of bulk update will be sent to your email.');
            $('#participantUpdateStatus').foundation('reveal', 'open');
          }
        },
        error: function( data ){
               $('i.fa-spinner').hide();
              data = $.parseJSON(data);
              modal.find('.error').append('<p class="warning">'+gettext('Please select file first.')+'</p>');
              $('#update_manager_data input[type=submit]').removeAttr('disabled');
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

      Dropzone.options.participantsManagerUpdate = {
      paramName: 'student_manager_list',
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
                  var values = {'limit': limit, 'lines': lines};
                  var linesLimitString = gettext("The .csv file has more then %(limit)s  rows: %(lines)s , please split it to more files!");
                  alert(interpolate(linesLimitString, values, true));
                  $('#update_manager_data .admin-form').find('.button-wrapper i').hide();
                  $('#update_manager_data #submitManagerUpdate').removeAttr('disabled');
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
        _this.on('success', function(file, data) {
            if(data.success) {
              $('i.fa-spinner').hide();
              $('#update_manager_data input[type=submit]').removeAttr('disabled');
              $('#participantUpdateStatus').foundation('reveal', 'open');
              $('#participantUpdateStatus .mainText').html(gettext('Report of bulk update will be sent to your email.'));
            }
        });
        _this.on("addedfile", function(file) {
          $('#update_manager_data .upload_stats').empty();
          $('#update_manager_data input[type=submit]').removeAttr('disabled');
        });
        _this.on("removedfile", function(file) {
          if (document.getElementById("id_student_field_list").files.length == 0) {
            $('#update_manager_data input[type=submit]').attr('disabled', 'disabled');
          }
        });
      }
    };
};

$('#closeParticipantUpdateStatus').on('click',function ()
{
  $('#participantUpdateStatus').foundation('reveal','close');
});
