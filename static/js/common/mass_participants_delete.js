massParticipantsDeleteInit = function() {
  if($('#id_student_delete_list').parents('#advanced_delete_modal').length > 0) {
    $(document).on('open.fndtn.reveal', '[data-reveal]', function () {
      $('i.fa-spinner').hide();
      setTimeout(function(){
        var element = $('#id_student_delete_list');
        var form = element.parents('form')
        element.val('');
        form.find('input[type=submit]').attr('disabled', 'disabled');
        form.find('#id_student_delete_list').attr('accept', '.csv');
        form.find('#delete-error-list').empty();
        form.find('#delete-confirm-error-list').empty();
        $('#delete_participants_success .send_email').hide();
        PopulateDeleteTemplateData();
        $(document).trigger('clearDropzone');
      }, 10);

      var mainContainer = $('#delete_participants_confirm_message');
      var deletionConfirmationCheckboxes = mainContainer.find('.massDeletionConfirmationCheckbox');
      var confirmButton = mainContainer.find('.confirmButton')

      deletionConfirmationCheckboxes.removeAttr('checked');
      confirmButton.addClass("disabled");

      deletionConfirmationCheckboxes.off().on('click', function() {
        if (deletionConfirmationCheckboxes.not(':checked').length == 0){
          confirmButton.removeClass('disabled');
        } else {
          confirmButton.addClass("disabled");
        }
      });
    });

    Dropzone.options.participantsDeleteCsvUpload = {
      paramName: 'student_delete_list',
      headers: { 'X-CSRFToken': $.cookie('apros_csrftoken')},
      autoProcessQueue: false,
      addRemoveLinks: true,
      acceptedFiles: '.csv',
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
          let user_count = response.user_count || 0;
          $('#delete_participants_confirm_message .user_count').text(user_count);
          $('#delete_participants_confirm_message').foundation('reveal', 'open');
          $('#id_file_url').val(response.file_url);
        });
        _this.on("addedfile", function(file) {
          $('#delete-error-list').empty();
          $('#advanced_delete_modal input[type=checkbox]').removeAttr('disabled');
          $('#advanced_delete_modal input[type=submit]').removeAttr('disabled');
        });
        _this.on("removedfile", function(file) {
          if (document.getElementById("id_student_delete_list").files.length == 0) {
            $('#advanced_delete_modal input[type=submit]').attr('disabled', 'disabled');
            $('#advanced_delete_modal input[type=checkbox]').attr('checked', false);
            $('#advanced_delete_modal input[type=checkbox]').attr('disabled', 'disabled');
          }
          $('#delete-error-list').empty();
        });
      }
    };
  }
  $('#id_student_delete_list').on("change", function(){
    if($('#id_student_delete_list').val() != '') {
      $('#advanced_delete_modal input[type=checkbox]').removeAttr('disabled');
      $('#advanced_delete_modal input[type=submit]').removeAttr('disabled');
    }
  });
  $('#advanced_delete_modal .admin-form').on('click', '#submitCSVDelete', function(e){
    e.preventDefault();
    var form = $(this).parents('.admin-form').find(".fileInputDelete");
    var modal = form.parent();
    modal.find('#delete-error-list').html('');
    $(this).attr('disabled', 'disabled');
    var _this = this;
    modal.find('.button-wrapper i').show();
    var file_input = document.getElementById("id_student_delete_list").files;
    if (file_input.length > 0) {
      var reader = new FileReader();
      reader.onload = function(e) {
        var options = {
          url: form.attr('action'),
          type: 'POST',
          dataType: 'json',
          cache: false,
          success: function(data) {
            let user_count = data.user_count || 0;
            $('#id_file_url').val(data.file_url);
            $('#delete_participants_confirm_message .user_count').text(user_count);
            $('#delete_participants_confirm_message').foundation('reveal', 'open');
          },
          error: function(data) {
            $('i.fa-spinner').hide();
            let errorMsg = data.responseText ? data.responseText : 'Failed to submit file.';
            modal.find('#delete-error-list').append('<p class="warning">'+gettext(errorMsg)+'</p>');
            $('#advanced_delete_modal input[type=submit]').removeAttr('disabled');
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
  $('#delete_participants_confirm_message').on('click', '.confirmButton', function(e) {
    e.stopPropagation();
    let form = $(this).parents('.admin-form').find("form");
    let options = {
      url: form.attr('action'),
      type: 'DELETE',
      cache: false,
      success: function(data, textStatus) {
        $('#delete_participants_success').foundation('reveal', 'open');
        if ($('#id_send_email').prop('checked')) {
          setTimeout(function() {
            $('#delete_participants_success .send_email').show();
          }, 10);
        }
      },
      error: function(xhr, textStatus, errorThrown) {
        $('#delete-confirm-error-list').append('<p class="warning">'+gettext('An error occurred submitting the request.')+'</p>');
      }
    };
    options.headers = { 'X-CSRFToken': $.cookie('apros_csrftoken')};
    form.ajaxSubmit(options);
  });
  $('#emailCompletionCheckboxId').on('change', function() {
    $('#id_send_email').prop('checked', this.checked);
    $('#id_send_email').val(this.checked ? 'True' : 'False');
  });
}

PopulateDeleteTemplateData = function()
{
  var data = [
    ['email'],
    ["personone@example.com"],
    ["persontwo@example.com"],
    ["personthree@example.com"]
  ];
  var csvContent = "data:text/csv;charset=utf-8,";
  data.forEach(function(infoArray, index){

     dataString = infoArray.join(",");
     csvContent += index < data.length ? dataString+ "\n" : dataString;

  });
  var encodedUri = encodeURI(csvContent);
  $('#advanced_delete_modal #deleteParticipantTemplate').attr("href", encodedUri);
};
