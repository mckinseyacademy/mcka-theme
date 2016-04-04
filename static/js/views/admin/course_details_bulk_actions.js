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
          $('#courseDetailsMainModal').find('.courseModalControl').find('.saveChanges').off().on('click', function()
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
              console.log(data);
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
    }
})