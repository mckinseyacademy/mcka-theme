Apros.views.CourseDetailsBulkActions = Backbone.View.extend({
    emailTemplates: [],
    initialize: function(options){
     this.courses_details_view = options.courses_details_view;
     this.courseDetails = options.courseDetails;
     this.courseId = options.courseId;
    },
    render: function()
    {
      var _this = this;
      $('#courseBulkActionsMainContainer').on('click','.hiddenButtonSplitModifier',function()
      {
        if (!$(this).hasClass('disabled'))
        {
          if ($('#dropBulkCourse').hasClass('open'))
          {
            $('#dropBulkCourse').removeClass('open');
            $('#dropBulkCourse').hide();
          }
          else
          {
            $('#dropBulkCourse').addClass('open');
            $('#dropBulkCourse').show();
          }
        }
        else
        {
          if ($('#dropBulkCourse').hasClass('open'))
          {
            $('#dropBulkCourse').removeClass('open');
            $('#dropBulkCourse').hide();
          }
        }
      });
      var statusUpdaterIntervalId = null;
      _this.initializeEmailTemplateListeners();
      var companyAdminFlag = $('#mainCourseDetailsWrapper').attr('admin-flag');
      if (companyAdminFlag == 'False' || companyAdminFlag == "" || companyAdminFlag == null || companyAdminFlag == false)
      {
        EmailTemplatesManager('GET');
      }
      $('#courseBulkActionsMainContainer').on('click','.bulkEmailSelectedParticipants',function()
      {
        if ($(this).hasClass('disabled'))
          return;
        var modal = $('#courseDetailsBulkEmail');
        modal.one('opened.fndtn.reveal', function(){
          var modalContainer = modal.parent();
          modalContainer.find('.reveal-modal-bg').attr('style', function(i,s) { return s + 'z-index: 1001 !important;' });
          modal.attr('style', function(i,s) { return s + 'z-index: 1002 !important;' });
          tinymce.init({
            selector: '#email_editor',
            theme: 'modern',
            file_browser_callback: function(field_name, url, type, win) {
                if(type=='image') {
                  $('#hidden_file_upload_form input').attr('accept',"image/*");
                  $(document).one("s3_files_uploaded",function(event, data){
                    alert("File successfully uploaded!");
                    $('#hidden_file_upload_form input').val("");
                    if (data["urls"].length)
                      $('#'+field_name).val(data["urls"][0]);
                  });
                  $('#hidden_file_upload_form input').one("change", function(e)
                  {
                    if ($(this).val())
                      S3FileUploader(this.files);
                  });
                  $('#hidden_file_upload_form input').click();
                }
            },
            height: 500,
            menubar:false,
            statusbar: false,
            plugins: [
              'autolink lists link image charmap print preview hr anchor pagebreak',
              'searchreplace wordcount visualblocks visualchars code fullscreen',
              'insertdatetime media nonbreaking save table contextmenu directionality',
              'paste textcolor colorpicker textpattern imagetools'
            ],
            toolbar1: 'insertfile undo redo | styleselect | bold italic underline forecolor backcolor | alignleft aligncenter alignright alignjustify | bullist numlist | link image | code'
          });
        });
        modal.off('change', '.templateNameValue select').on('change', '.templateNameValue select', function()
        {
          var editor = tinymce.get('email_editor');
          var subject = modal.find('.emailSubjectValue input')
          subject.val('')
          editor.setContent('');
          for (var i = 0; i < _this.emailTemplates.length; i++)
          {
            if (parseInt(_this.emailTemplates[i].pk) == parseInt($(this).val()))
            {
              subject.val(_this.emailTemplates[i].subject)
              editor.setContent(_this.emailTemplates[i].body);
              break;
            }
          }
          modal.find('.emailModalControl').find('.sendEmail').removeClass("disabled");
        });
        modal.find('.templateNameValue select option:eq(0)').prop('selected', true);
        modal.find('.fromEmailValue input').val("support@mckinseyacademy.com");
        modal.find('.emailSubjectValue input').val("");
        var controlButtonContainer = modal.find('.emailModalControl');
        controlButtonContainer.find('.sendEmail').addClass('disabled');
        modal.on('change', 'input', function()
        {
          controlButtonContainer.find('.sendEmail').removeClass('disabled');
        })
        modal.foundation('reveal', 'open');
      });
      $('#courseBulkActionsMainContainer').on('click','.bulkUnenrollFromCourse',function()
      {
        if ($(this).hasClass('disabled'))
          return;
        var selectedRowsIdsLen = _this.courses_details_view.coursesListDetailsViewGrid.selectedRows.length;
        $('#courseDetailsMainModal').find('.courseModalTitle').text('Unenroll Participants');
        $('#courseDetailsMainModal').find('.courseModalStatus').text('Selected: '+selectedRowsIdsLen+', Successful: 0, Failed: 0');
        $('#courseDetailsMainModal').find('.courseModalDescription').text('Unenroll all selected participants from this course?');
        $('#courseDetailsMainModal').find('.courseModalContent').empty();
        $('#courseDetailsMainModal').find('.courseModalControl').find('.cancelChanges').off().on('click', function()
        {
          if (statusUpdaterIntervalId !== null)
          {
            $('#courseDetailsMainModal .courseModalStatus').parent().find('.loadingIcon').addClass('hidden');
            clearInterval(statusUpdaterIntervalId);
            statusUpdaterIntervalId = null;
          }
          $('#courseDetailsMainModal').find('a.close-reveal-modal').trigger('click');
        });
        if(_this.courses_details_view.coursesListDetailsViewGrid.selectedRows.length === 0) {
          alert("You need to select at least one participant to be able to apply bulk actions.")
        }
        else {
          var saveButton = $('#courseDetailsMainModal').find('.courseModalControl').find('.saveChanges');
          saveButton.text('Unenroll');
          saveButton.off().on('click', function()
          {
            var selectedRowsIds = _this.courses_details_view.coursesListDetailsViewGrid.selectedRows;
            var dictionaryToSend = {type:'unenroll_participants', list_of_items:[]};
            for (selectedRowsIndex in selectedRowsIds)
            {
              var id = selectedRowsIds[selectedRowsIndex];
              dictionaryToSend.list_of_items.push(id);
            }
            var url = ApiUrls.course_details+'/'+_this.courseId;
            var options = {
              url: url,
              data: JSON.stringify(dictionaryToSend),
              processData: false,
              type: "POST",
              dataType: "json"
            };

            options.headers = { 'X-CSRFToken': $.cookie('apros_csrftoken')};
            $.ajax(options)
            .done(function(data) {
              if (data['status'] == 'ok')
              {
                statusUpdaterIntervalId = _this.courses_details_view.realtimeStatus(url, '#courseDetailsMainModal .courseModalStatus', data['task_id']);
              }
              })
            .fail(function(data) {
              console.log("Ajax failed to fetch data");
              console.log(data);
              })
          });
          $('#courseDetailsMainModal').foundation('reveal', 'open');
        }
      });
      $('#courseBulkActionsMainContainer').on('click','.bulkChangeStatus',function()
      {
        if ($(this).hasClass('disabled'))
          return;
        var selectedRowsIdsLen = _this.courses_details_view.coursesListDetailsViewGrid.selectedRows.length;
        $('#courseDetailsMainModal').find('.courseModalTitle').text('Change Status');
        $('#courseDetailsMainModal').find('.courseModalStatus').text('Selected: '+selectedRowsIdsLen+', Successful: 0, Failed: 0');
        $('#courseDetailsMainModal').find('.courseModalDescription').text('Change status of all selected participants to:');
        $('#courseDetailsMainModal').find('.courseModalContent').html(
          '<input type="radio" name="status" value="Active" id="participantCheckbox"><label for="participantCheckbox">Active</label>'+
          '<input type="radio" name="status" value="Observer" id="observerCheckbox"><label for="observerCheckbox">Observer</label>'+
          '<input type="radio" name="status" value="TA" id="taCheckbox"><label for="taCheckbox">TA</label>'
        );
        $('#courseDetailsMainModal').find('.courseModalControl').find('.cancelChanges').off().on('click', function()
        {
          if (statusUpdaterIntervalId !== null)
          {
            $('#courseDetailsMainModal .courseModalStatus').parent().find('.loadingIcon').addClass('hidden');
            clearInterval(statusUpdaterIntervalId);
            statusUpdaterIntervalId = null;
          }
          $('#courseDetailsMainModal').find('a.close-reveal-modal').trigger('click');
        });
        if(_this.courses_details_view.coursesListDetailsViewGrid.selectedRows.length === 0) {
          alert("You need to select at least one participant to be able to apply bulk actions.")
        }
        else {
          var saveButton = $('#courseDetailsMainModal').find('.courseModalControl').find('.saveChanges');
          saveButton.text('Save Changes');
          saveButton.addClass('disabled');
          saveButton.attr('disabled','disabled');
          $("#courseDetailsMainModal input[type='radio']").on('change', function(){
            saveButton.removeClass('disabled');
            saveButton.removeAttr('disabled');
          })
          saveButton.off().on('click', function()
          {
            if ($(this).hasClass('disabled'))
              return;
            saveButton.addClass('disabled');
            saveButton.attr('disabled','disabled');
            var selectedRowsIds = _this.courses_details_view.coursesListDetailsViewGrid.selectedRows;
            var selectedVal = "";
            var selected = $("#courseDetailsMainModal input[type='radio']:checked");
            if (selected.length > 0) {
                selectedVal = selected.val();
            }
            else
            {
              alert('You need to select status!');
              return;
            }
            var dictionaryToSend = {type:'status_change', new_status: selectedVal, list_of_items:[]};
            for (selectedRowsIndex in selectedRowsIds)
            {
              var id = selectedRowsIds[selectedRowsIndex];
              var selectedModel = _this.courseDetails.fullCollection.get(id);
              var item ={ id: id, existing_roles: selectedModel.attributes.user_status};
              dictionaryToSend.list_of_items.push(item);
            }
            var url = ApiUrls.course_details+'/'+_this.courseId;
            var options = {
              url: url,
              data: JSON.stringify(dictionaryToSend),
              processData: false,
              type: "POST",
              dataType: "json"
            };

            options.headers = { 'X-CSRFToken': $.cookie('apros_csrftoken')};
            $.ajax(options)
            .done(function(data) {
              if (data['status'] == 'ok')
              {
                statusUpdaterIntervalId = _this.courses_details_view.realtimeStatus(url, '#courseDetailsMainModal .courseModalStatus', data['task_id']);
              }
              })
            .fail(function(data) {
              console.log("Ajax failed to fetch data");
              console.log(data);
              })
          });
          $('#courseDetailsMainModal').foundation('reveal', 'open');
        }
      });
      $('#courseBulkActionsMainContainer').on('click','.bulkEnrollInNewCourse',function()
      {
        if ($(this).hasClass('disabled'))
          return;
        var selectedRowsIdsLen = _this.courses_details_view.coursesListDetailsViewGrid.selectedRows.length;
        $('#courseDetailsMainModal').find('.courseModalTitle').text('Select Course');
        $('#courseDetailsMainModal').find('.courseModalStatus').text('Selected: '+selectedRowsIdsLen+', Successful: 0, Failed: 0');
        $('#courseDetailsMainModal').find('.courseModalDescription').text(''+selectedRowsIdsLen+' Participants will be enroll in course selected below.');
        $('#courseDetailsMainModal').find('.courseModalContent').html(
          '<div class="row enrollParticipants">' +
          '<div class="large-6 columns enrollParticipantsCourse">' +
          '<p class="labelUnirvesal">Course</p>' +
          '<input type="text" value="" name="course" maxlength="60">' +
          '</div>' +
          '<div class="large-6 columns enrollParticipantsStatus">' +
          '<p class="labelUnirvesal">Status</p>' +
          '<select name="status">' +
          '<option value="Active">Active</option>' +
          '<option value="Observer">Observer</option>' +
          '<option value="TA">TA</option></select>' +
          '</div></div>'
        );
        var url = ApiUrls.participant_courses_get_api();
        InitializeAutocompleteInput(url, '.enrollParticipantsCourse input');
        $('#courseDetailsMainModal').find('.courseModalControl').find('.cancelChanges').off().on('click', function()
        {
          if (statusUpdaterIntervalId !== null)
          {
            $('#courseDetailsMainModal .courseModalStatus').parent().find('.loadingIcon').addClass('hidden');
            clearInterval(statusUpdaterIntervalId);
            statusUpdaterIntervalId = null;
          }
          $('#courseDetailsMainModal').find('a.close-reveal-modal').trigger('click');
        });
        if(_this.courses_details_view.coursesListDetailsViewGrid.selectedRows.length === 0) {
          alert("You need to select at least one participant to be able to apply bulk actions.")
        }
        else {
          var saveButton = $('#courseDetailsMainModal').find('.courseModalControl').find('.saveChanges');
          saveButton.text('Enroll Participants');
          saveButton.attr('disabled', 'disabled');
          saveButton.addClass('disabled');
          $(document).on('autocomplete_found', function(event, input){
            var course_id = $('.enrollParticipantsCourse input').attr('data-id');
            if (course_id){
              input.parents('#courseDetailsMainModal').find('.courseModalControl .saveChanges').removeAttr('disabled');
              input.parents('#courseDetailsMainModal').find('.courseModalControl .saveChanges').removeClass('disabled');
            }
          });
          $(document).on('autocomplete_not_found', function(event, input){
            input.parents('#courseDetailsMainModal').find('.courseModalControl .saveChanges').attr('disabled', 'disabled');
            input.parents('#courseDetailsMainModal').find('.courseModalControl .saveChanges').addClass('disabled');
          });
          saveButton.off().on('click', function()
          {
            if ($(this).hasClass('disabled'))
              return;
            var selectedRowsIds = _this.courses_details_view.coursesListDetailsViewGrid.selectedRows;
            var selectedVal = "";
            var selected = $('.enrollParticipantsStatus select');
            if (selected.length > 0) {
                selectedVal = selected.val();
                if(!selectedVal){
                  alert('You need to select status!');
                  return;
                }
            }
            else
            {
              alert('You need to select status!');
              return;
            }
            var course_id = $('.enrollParticipantsCourse input').attr('data-id');
            if (!course_id){
              alert('You need to select course!');
              return;
            }
            if (course_id.length == 0) {
              alert('You need to select course!');
              return;
            }
            var dictionaryToSend = {type:'enroll_participants', new_status: selectedVal, list_of_items:[], course_id: course_id};
            for (selectedRowsIndex in selectedRowsIds)
            {
              var id = selectedRowsIds[selectedRowsIndex];
              var item ={ id: id};
              dictionaryToSend.list_of_items.push(item);
            }
            var url = ApiUrls.course_details+'/'+_this.courseId;
            var options = {
              url: url,
              data: JSON.stringify(dictionaryToSend),
              processData: false,
              type: "POST",
              dataType: "json"
            };

            options.headers = { 'X-CSRFToken': $.cookie('apros_csrftoken')};
            saveButton.attr('disabled', 'disabled');
            saveButton.addClass('disabled');
            $.ajax(options)
            .done(function(data) {
              if (data['status'] == 'ok')
              {
                statusUpdaterIntervalId = _this.courses_details_view.realtimeStatus(url, '#courseDetailsMainModal .courseModalStatus', data['task_id'], _this, course_id);
              }
              })
            .fail(function(data) {
              console.log("Ajax failed to fetch data");
              console.log(data);
              })
          });
          $('#courseDetailsMainModal').foundation('reveal', 'open');
        }
      });
      /* utility function for modal attributes update */
      function updateModalAttrs(title, status, saveButtonText) {
          $('#courseDetailsMainModal').find('.courseModalTitle').text(title);
          $('#courseDetailsMainModal').find('.courseModalStatus').text(status);
      }
      /* utility function for modal save button attributes update */
      function updateSaveButtonAttrs(text, disabled, dataurl){
        var saveButton = $('#courseDetailsMainModal').find('.courseModalControl').find('.saveChanges');

        if(text)
          saveButton.text(text);
        if(disabled){
          saveButton.attr('disabled', 'disabled');
          saveButton.addClass('disabled');
        }
        if(dataurl)
          saveButton.attr('data-download-url', dataurl);
      }
      /**
       * Initiates a backend background task and its periodical status check
      */
      function backendCSVDownloader(params){
          var courseId = $("#courseDetailsDataWrapper").attr("data-id");
          var url = ApiUrls.admin_bulk_task; 
          var dictionaryToSend = {type:params.type, course_id: courseId};
          
          // if company page; pass in company id
          var companyPageFlag = $('#courseDetailsDataWrapper').attr('company-page');
          if (companyPageFlag == 'True'){
            var companyId = $('#courseDetailsDataWrapper').attr('company-id');
            dictionaryToSend['company_id'] = companyId;
          }
        
          updateModalAttrs(params.modalTitle || 'Download', 'Progress : 0%');
          updateSaveButtonAttrs('Download CSV File', true, null);

          var options = {
            url: url,
            data: JSON.stringify(dictionaryToSend),
            processData: false,
            type: "POST",
            dataType: "json"
          };
          options.headers = { 'X-CSRFToken': $.cookie('apros_csrftoken')};
        
          $.ajax(options)
          .done(function(data, textStatus, xhr) {
            if (xhr.status === 201){
              updateSaveButtonAttrs(null, null, params.downloadLink + data['task_id'] + '/?' + params.linkParams);
              statusUpdaterIntervalId = _this.courses_details_view.csvDownloadStatus(
                url, '#courseDetailsMainModal .courseModalStatus',
                data['task_id'], _this, courseId
              );
            }
          })
          .fail(function(data) {
            console.log("Ajax failed to fetch data");
            console.log(data);
          })
        
          $('#courseDetailsMainModal').foundation('reveal', 'open');
      }
      $('#courseBulkActionsMainContainer').on('click','.bulkExportNotifData',function(){
        if ($(this).hasClass('disabled'))
          return;

        var courseId = $("#courseDetailsDataWrapper").attr("data-id");
        var filename = '' + $('#courseDetailsDataWrapper').attr('data-name')
                .replace(/ /g,'_') + '_push_notification_data.csv';

        if($(this).hasClass('allselected')){
            // transfer control to backend downloader in case of select-all
            backendCSVDownloader({
              type: 'push_notifications_data', modalTitle: 'Download Notifications CSV',
              downloadLink: '/admin/download_task_generated_csv/',
              linkParams: 'task_name=push_notifications_data&file_name=' + filename
            });
            return;
        }

        var selectedRowsIds = _this.courses_details_view.coursesListDetailsViewGrid.selectedRows;

        var items = [];
        for (selectedRowsIndex in selectedRowsIds) {
          var id = selectedRowsIds[selectedRowsIndex];

          var item = {
            'attribute_type': 'named_user',
            'attribute': id
          };
          items.push(item);
        }


        downloadCSV({data: items, filename: filename, header: false});

      });
      
      $('#courseBulkActionsMainContainer').on('click','.bulkExportStats',function()
      {
        var courseId = $("#courseDetailsDataWrapper").attr("data-id");
        var filename = '' + $('#courseDetailsDataWrapper').attr('data-name').replace(/ /g,'_') + '_users_stats.csv';

        
        if($(this).hasClass('allselected')){
            // transfer control to backend downloader in case of select-all
            backendCSVDownloader({
              type: 'participants_csv_data', modalTitle: 'Download Participants',
              downloadLink: '/admin/download_task_generated_csv/',
              linkParams: 'task_name=participants_stats&file_name=' + filename
            });
            return;
        }

        if ($(this).hasClass('disabled'))
        {
          return;
        }
        var selectedRowsIds = _this.courses_details_view.coursesListDetailsViewGrid.selectedRows;

        var modelsList = _this.courseDetails.fullCollection.models;

        items = []
        for (selectedRowsIndex in selectedRowsIds)
        {
          var id = selectedRowsIds[selectedRowsIndex];
          var selectedModel = _this.courseDetails.fullCollection.get(id);
          var last_login = selectedModel.attributes.custom_last_login.split(',')[1];
          var progress = '' + parseInt(selectedModel.attributes.progress) + '%';
          var proficiency = '' + parseInt(selectedModel.attributes.proficiency) + '%';
          var engagement = '' + parseInt(selectedModel.attributes.engagement)
          var activation_link = selectedModel.attributes.activation_link;
          var item =
          {
            'id': id,
            'First name': selectedModel.attributes.first_name,
            'Last name': selectedModel.attributes.last_name,
            'Username': selectedModel.attributes.username,
            'Email': selectedModel.attributes.email,
            'Company': selectedModel.attributes.organizations_display_name,
            'Status': selectedModel.attributes.custom_user_status,
            'Activated': selectedModel.attributes.custom_activated,
            'Last login': last_login,
            'Progress': progress,
            'Proficiency': proficiency,
            'Engagement': engagement,
            'Activation Link': activation_link,
            'Country': selectedModel.attributes.country
          };
          items.push(item);
        }

        for (var i=0; i < modelsList.length; i++)
        {
          if (modelsList[i].attributes.groupworks.length)
          {
            for (var groupworkIndex = 0; groupworkIndex < modelsList[i].attributes.groupworks.length; groupworkIndex++)
            {
              groupworkData = modelsList[i].attributes.groupworks[groupworkIndex];
              for(var j=0; j < items.length; j++)
              {
                var selected = _this.courseDetails.fullCollection.get(items[j]['id']);
                var label = 'Group Work: ' + groupworkData.label;
                if (selected.attributes.groupworks.length)
                {
                  items[j][label] = '' + parseInt(selected.attributes.groupworks[groupworkIndex].percent) + '%';
                }
                else
                {
                  items[j][label] = '' + parseInt('000') + '%';
                }
              }
            }
            break;
          }
        }

        for (var i=0; i < modelsList.length; i++)
        {
          if (modelsList[i].attributes.assessments.length)
          {
            for (var assessmentIndex = 0; assessmentIndex < modelsList[i].attributes.assessments.length; assessmentIndex++)
            {
              assessmentData = modelsList[i].attributes.assessments[assessmentIndex];
              for(var j=0; j < items.length; j++)
              {
                var selected = _this.courseDetails.fullCollection.get(items[j]['id']);
                var label = 'Assessment: ' + assessmentData.label;
                if (selected.attributes.assessments.length)
                {
                  items[j][label] = '' + parseInt(selected.attributes.assessments[assessmentIndex].percent) + '%';
                }
                else
                {
                  items[j][label] = '' + parseInt('000') + '%';
                }
              }
            }
            break;
          }
        }

        downloadCSV({data: items, filename: filename});

      });
    },
    /** Called back when CSV generation is completed */
    csvDownloadCallback: function functionName(_this, data) {
      if(data['values'].state == 'FAILURE'){
        $('#courseDetailsMainModal').find('.courseModalContent')
            .text('Task failed to execute. Please retry later.');
        return;
      }
      var saveButton = $('#courseDetailsMainModal').find('.courseModalControl').find('.saveChanges');
      saveButton.removeAttr('disabled');
      saveButton.removeClass('disabled');

      saveButton.on('click', function(){
        window.location.href = saveButton.attr('data-download-url');
        $('#courseDetailsMainModal').find('a.close-reveal-modal').trigger('click');
      });
    },
    createConfirmationScreenOnCourseDetails: function(_this, course_id) {
      if ($(this).hasClass('disabled'))
        return;
      var selectedRowsIds = _this.courses_details_view.coursesListDetailsViewGrid.selectedRows;
      var selectedRowsIdsLen = selectedRowsIds.length;
      $('#courseDetailsMainModal').find('.courseModalTitle').text('Successfully Enrolled in 1 Course');
      $('#courseDetailsMainModal').find('.courseModalStatus').empty();
      $('#courseDetailsMainModal').find('.courseModalDescription').text('What would you like to do now?');
      $('#courseDetailsMainModal').find('.courseModalContent').html(
        '<a href="#" target="_blank">Send Course Intro Email</a><br><br>' +
        '<a href="/admin/courses/'+course_id+'" target="_blank">Go to '+course_id+' Course</a><br><br>' +
        '<a href="#" class="enrollThisUsersInNewCourse">Enroll this list in another course</a><br><br>'
      );
      $('#courseDetailsMainModal').on('click', '.enrollThisUsersInNewCourse', function(){
        $('#courseBulkActionsMainContainer').find('.bulkEnrollInNewCourse').trigger('click');
      });
      if(selectedRowsIdsLen == 0) {
        alert("You need to select at least one participant to be able to apply bulk actions.")
      }
      else {
        var saveButton = $('#courseDetailsMainModal').find('.courseModalControl').find('.saveChanges');
        saveButton.removeAttr('disabled');
        saveButton.removeClass('disabled');
        saveButton.text("I'm Done");
        saveButton.off().on('click', function()
        {
          $('#courseDetailsMainModal').find('a.close-reveal-modal').trigger('click');
        });
        $('#courseDetailsMainModal').foundation('reveal', 'open');
      }
    },
    initializeEmailTemplateListeners: function()
    {
      var _this = this;
      var modal = $('#courseDetailsBulkEmail');
      $(document).on('email_templates_fetched', function(event, data)
      {
        _this.emailTemplates = data.data;
      });
      $(document).on('email_template_deleted', function(event, data)
      {
        modal.find('.templateNameValue select').find('option[value="'+data.pk+'"]').remove();
        modal.find('.templateNameValue select').trigger('change');
        alert('Successfully deleted template!');
      });
      $(document).on('email_template_added', function(event, data)
      {
        modal.find('.templateNameValue select').append('<option value="'+data.data.pk+'">'+data.data.title+'</option>')
        _this.emailTemplates.push(data.data);
        modal.find('.templateNameValue select').trigger('change');
        alert('Successfully added new template!');
      });
      $(document).on('email_template_updated', function(event, data)
      {
        modal.find('.templateNameValue select').find('option[value="'+data.data.pk+'"]').text(data.data.title);
        for (var i = 0; i < _this.emailTemplates.length; i++)
        {
          if (parseInt(_this.emailTemplates[i].pk) == parseInt(data.data.pk))
          {
            _this.emailTemplates[i] = data.data;
            break;
          }
        }
        alert('Successfully updated template!');
      });
      $(document).on('email_sent', function(e, data)
      {
        if (data['type'] == 'preview')
          CreateNicePopup("Email Preview Success!", 'Successfully sent preview email!');
        else
        {
          CreateNicePopup("Email Success!", 'Successfully sent email!');
          modal.foundation('reveal', 'close');
        }

      });

      modal.on('closed.fndtn.reveal', function(){
          tinymce.get('email_editor').setContent("");
          tinymce.remove('#email_editor');
      });
      var controlButtonContainer = modal.find('.emailModalControl');
      var templateButtonContainer = modal.find('.templateControlButtons');
      controlButtonContainer.on('click', '.sendEmail', function(e)
      {
        if($(this).hasClass('disabled'))
          return;
        $(this).addClass('disabled');
        var sender = modal.find('.fromEmailValue input').val();
        var body = tinymce.get('email_editor').getContent();
        var subject = modal.find('.emailSubjectValue input').val();
        var bbgrid_table = _this.courses_details_view.coursesListDetailsViewGrid;
        var selectedRowsIds = bbgrid_table.selectedRows;
        var to_email_list = [];
        var student_list = [];
        var user_data = null
        for (var i = 0; i<selectedRowsIds.length; i++ )
        {
          user_data = bbgrid_table.collection.get(selectedRowsIds[i]).attributes;
          to_email_list.push(user_data.email);
          var user_stats = {"id": user_data.id, "progress": user_data.progress, "proficiency": user_data.proficiency, "email": user_data.email,
                            "organization_name":user_data.organizations_display_name, "first_name": user_data.first_name, "last_name": user_data.last_name};
          student_list.push(user_stats);
        }
        var course_id = $("#courseDetailsDataWrapper").attr("data-id");
        var  template_id = modal.find('.templateNameValue select').val();
        if (template_id == 'none')
          template_id = null;
        SendEmailManager(sender, subject, to_email_list, body, template_id, false, {"course_id":course_id, "user_list":student_list});
      });
      controlButtonContainer.on('click', '.previewEmail', function(e)
      {

        var email = CreatNicePrompt("Preview Email!","Please enter preview email!");
        $(document).one("dynamic_prompt_confirmed", function(e, email)
        {
          if (email != null)
          {
            var sender = modal.find('.fromEmailValue input').val();
            var body = tinymce.get('email_editor').getContent();
            var subject = modal.find('.emailSubjectValue input').val();
            var to_email_list = [];
            to_email_list.push(email)
            var  template_id = modal.find('.templateNameValue select').val();
            if (template_id == 'none')
              template_id = null;
            SendEmailManager(sender, subject, to_email_list, body, template_id, true);
          }
        })
      });
      templateButtonContainer.on('click', '.saveAsNewTemplate', function(e)
      {
        var subject = modal.find('.emailSubjectValue input').val();
        var title = prompt("Please enter new template name!", subject);
        var body = tinymce.get('email_editor').getContent();
        if (title != null)
        {
          EmailTemplatesManager('POST', "", title, subject, body);
        }
      });
      templateButtonContainer.on('click', '.updateTemplate', function(e)
      {
        var select = modal.find('.templateNameValue select');
        var selected_pk = select.val();
        if (selected_pk != 'none')
        {
          var subject = modal.find('.emailSubjectValue input').val();
          var title = select.find('option[value="'+selected_pk+'"]').text().trim();
          title = prompt("Please enter updated template name or leave the old one!", title);
          var body = tinymce.get('email_editor').getContent();
          if (title != null)
          {
            EmailTemplatesManager('PUT', selected_pk, title, subject, body);
          }
        }
      });
      templateButtonContainer.on('click', '.removeTemplate', function(e)
      {
        var selected_pk = modal.find('.templateNameValue select').val();
        if (selected_pk != 'none')
        {
          var r = confirm("You are about to delete email template. Are you sure?");
          if (r == true)
            EmailTemplatesManager('DELETE', selected_pk);
        }
      });
    }
})
