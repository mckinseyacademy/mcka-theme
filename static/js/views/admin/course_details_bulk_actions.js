Apros.views.CourseDetailsBulkActions = Backbone.View.extend({
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
          saveButton.off().on('click', function()
          {
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
          saveButton.off().on('click', function()
          {
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
            $.ajax(options)
            .done(function(data) {
              console.log(data);
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
        saveButton.text("I'm Done");
        saveButton.off().on('click', function()
        {
          $('#courseDetailsMainModal').find('a.close-reveal-modal').trigger('click');
        });
        $('#courseDetailsMainModal').foundation('reveal', 'open');
      }
    }
})