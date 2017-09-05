  Apros.views.CourseDetailsView = Backbone.View.extend({

    coursesListDetailsViewGrid: {},
    generatedGridColumns:
    [
      { title: 'Name', index: true, name: 'username', titleAttribute: 'full_name',
      actions: function(id, attributes)
      {
        var companyPageFlag = $('#courseDetailsDataWrapper').attr('company-page');
        if (companyPageFlag == 'False')
        {
          return '<a href="/admin/participants/' + attributes['id'] + '" target="_self">' + attributes['username'] + '</a>';
        }
        else
        {
          var companyAdminFlag = $('#courseDetailsDataWrapper').attr('admin-flag');
          if (companyAdminFlag == 'False')
          {
            return '<a href="/admin/participants/' + attributes['id'] + '" target="_self">' + attributes['username'] + '</a>';
          }
          else
          {
            var companyId = $('#courseDetailsDataWrapper').attr('company-id');
            return '<a href="/admin/companies/' + companyId + '/participants/' + attributes['id'] + '" target="_self">' + attributes['username'] + '</a>';
          }
        }
      }},
      { title: 'Email', index: true, name: 'email' },
      { title: 'Company', index: true, name: 'organizations_display_name'},
      { title: 'Status', index: true, name: 'custom_user_status'},
      { title: 'Activated', index: true, name: 'custom_activated'},
      { title: 'Last Log In', index: true, name: 'custom_last_login',
      actions: function(id, attributes)
      {
        if (attributes['custom_last_login'] != '-' && attributes['custom_last_login'] != '' && typeof attributes['custom_last_login'] != 'undefined')
        {
         var last_login = attributes['custom_last_login'].split(',')[0].split('/');
            return '' + last_login[1] + '/' + last_login[2] + '/' + last_login[0];
        }
        return attributes['custom_last_login'];
      }},
      { title: 'Progress', index: true, name: 'progress', actions: function(id, attributes)
      {
        value = attributes['progress'];
        if (value == '-')
          return value;
        return '' + parseInt(value) + '%';
      }},
      { title: 'Proficiency', index: true, name: 'proficiency', actions: function(id, attributes)
      {
        value = attributes['proficiency'];
        if (value == '-')
          return value;
        return '' + parseInt(value) + '%'; 
      }},
      { title: 'Activation Link', index: true, name: 'activation_link', actions: function (id, attributes) {
        var value = attributes['activation_link'];
        
        if(value != '')
            value = '<a href="' + value + '">' + 'Activation Link' + '</a>';

        return value;
      }},
      { title: 'Username', index: true, name: 'username' },
      { title: 'Country', index: true, name: 'country'}
    ],
    initialize: function(){
      InitializeTooltipOnPage();
      var _this = this;
      var companyPageFlag = $('#courseDetailsDataWrapper').attr('company-page');
      if (companyPageFlag == 'True')
      {
        var companyId = $('#courseDetailsDataWrapper').attr('company-id');
        this.collection.updateCompanyQuerryParams(companyId);
      }
      var count = course_details_count_all_users;
      this.collection.updateCountQuerryParams(count);
      this.collection.fetch({success:function(collection, response, options){
          _this.updateColumns(_this.collection, _this.coursesListDetailsViewGrid);
          cloneHeader('#courseDetailsParticipantsGrid');
        }});
    },
    render: function(){
      var _this = this;
      var companyAdminFlag = $('#courseDetailsDataWrapper').attr('admin-flag');
      var courseId = $('#courseDetailsDataWrapper').attr('data-id');
      var multiSelectFlag = true;
      if (companyAdminFlag == 'True')
      {
        multiSelectFlag = false;
        var index = 0;
        for (var i=0; i < _this.generatedGridColumns.length; i++)
        {
          if (_this.generatedGridColumns[i]['title'] == 'Company')
          {
            index = i;
          }
        }
        _this.generatedGridColumns.splice(index,1);
      }
      var coursesListDetailsViewGrid = {}
      coursesListDetailsViewGrid['partial_collection'] = this.collection;
      coursesListDetailsViewGrid = new bbGrid.View({
        container: this.$el,
        multiselect: multiSelectFlag,
        enableSearch: true,
        collection: this.collection.fullCollection,
        onRowClick: function()
        {
          // for select-all bind export csv functionalities to a backend downloader
          if($('.bbGrid-grid-head-holder input[type=checkbox]:first').is(':checked')){
            $('a.bulkExportStats').addClass('allselected');
            $('a.bulkExportNotifData').addClass('allselected');
          }else{
            $('a.bulkExportStats').removeClass('allselected');
            $('a.bulkExportNotifData').removeClass('allselected');
          }

          if (this.selectedRows.length > 0)
          {
            if ($('#courseBulkActionsMainContainer').hasClass('disabled'))
            {
              $('#courseBulkActionsMainContainer').removeClass('disabled');
              $('#courseBulkActionsMainContainer').find('.bulkButton').each(function()
              {
                $(this).removeClass('disabled');
              });
            }
          }
          else
          {
            if (!$('#courseBulkActionsMainContainer').hasClass('disabled'))
            {
              $('#courseBulkActionsMainContainer').addClass('disabled');
              $('#courseBulkActionsMainContainer').find('.bulkButton').each(function()
              {
                $(this).addClass('disabled');
              });
            }
            if ($('#dropBulkCourse').hasClass('open'))
            {
              $('#dropBulkCourse').removeClass('open');
              $('#dropBulkCourse').hide();
            }
          }
        },
        colModel: _this.generatedGridColumns
      });

      coursesListDetailsViewGrid['partial_collection'] = this.collection;
      this.coursesListDetailsViewGrid = coursesListDetailsViewGrid;
      this.$el.find('.bbGrid-container').on('scroll', { extra : this}, this.fetchPages);
      $(document).on('onSearchEvent', { extra : this}, this.onSearchEvent);
      $(document).on('onClearSearchEvent', { extra : this}, this.onClearSearchEvent);

      $('#mainCourseDetailsWrapper').on('click', '.courseTagsIcon', function()
      {
        var course_tags_modal = $('#courseTagsModal');
        var errorMessage = course_tags_modal.find('.errorMessage');
        var addTagButton = course_tags_modal.find('.addTagButton');
        var courseTagsInput = course_tags_modal.find('.courseTagsInput');
        errorMessage.empty();
        addTagButton.addClass('disabled');
        courseTagsInput.val('');
        var tag_id = 0;
        course_tags_modal.find('.newTagCreationPopup').hide();
        var course_id = $('#courseDetailsDataWrapper').attr('data-id');
        course_tags_modal.find('.courseTagsModalControl').find('.closeModal').off().on('click', function()
        {
          course_tags_modal.find('a.close-reveal-modal').trigger('click');
        });
        var url = ApiUrls.tags + '?course_id=' + course_id;
        InitializeAutocompleteInput(url, '.courseTagsList input');
        $(document).on('autocomplete_found', function(event, input)
        {
          if (input.parent().hasClass('courseTagsList'))
          {
            errorMessage.empty();
            _this.manageNewTagPopup(input, false);
            addTagButton.removeClass('disabled');
          }
        });
        $(document).on('autocomplete_not_found', function(event, input)
        {
          if (input.parent().hasClass('courseTagsList'))
          {
            errorMessage.empty();
            _this.manageNewTagPopup(input, true);
          }
        });
        course_tags_modal.on('click', '.addTagButton', function()
        {
          if ($(this).hasClass('disabled'))
            return;
          $(this).addClass('disabled');
          if (courseTagsInput.attr('data-id'))
          {
            tag_id = courseTagsInput.attr('data-id');
            _this.addTagToCourse(tag_id, course_id);
          }
          else
          {
            var internalAdminFlag = $('#courseDetailsDataWrapper').attr('internal-flag');
            if (internalAdminFlag == 'False')
            {
              var tag_name = courseTagsInput.val().trim();
              if (tag_name.toLowerCase() == 'internal')
              {
                tag_name = tag_name.toUpperCase();
              }
              var data = {"name": tag_name};
              var url = ApiUrls.tags;
              var options = {
                url: url,
                data: data,
                type: "POST",
                dataType: "json"
              };
              options.headers = { 'X-CSRFToken': $.cookie('apros_csrftoken')};
              $.ajax(options)
              .done(function(data) {
                if (data['status'] == 'ok')
                {
                  tag_id = parseInt(data['id']);
                  _this.addTagToCourse(tag_id, course_id);
                }
                else if (data['status'] == 'error')
                {
                  alert("Couldn't create new tag!")
                  return;
                }
                else if(data['status'] == 'errorAlreadyExist')
                {
                  $('#courseTagsModal').find('.errorMessage').text(data['message']);
                }
              })
              .fail(function(data) {
                console.log("Ajax failed to fetch data");
              });
            }
            else
            {
              $('#courseTagsModal').find('.errorMessage').text("You don't have permission to create a new tag, please select one from the list!");
            }
          }
        });
        course_tags_modal.foundation('reveal', 'open');
      });
      $('#mainCourseDetailsWrapper').on('mouseover', '.courseDetailsTagsList', function()
      {
        var course_id = $('#courseDetailsDataWrapper').attr('data-id');
        var tag_id = $(this).attr('data-id');
        var _thisTag = this;
        $(this).find('.courseTagsDeleteIcon').show();
        $(this).off('click').on('click', '.courseTagsDeleteIcon', function(event)
        {
          event.stopPropagation();
          var url = ApiUrls.courses_list + '/' + course_id + '/tags?tag_id=' + tag_id;
          var options = {
            url: url,
            type: "DELETE",
            dataType: "json"
          };
          options.headers = { 'X-CSRFToken': $.cookie('apros_csrftoken')};
          $.ajax(options)
          .done(function(data) {
            if (data['status'] == 'ok')
            {
              _thisTag.remove();
            }
            else if (data['status'] == 'error')
            {
              alert("Couldn't delete tag!")
              return;
            }
          })
          .fail(function(data) {
            console.log("Ajax failed to fetch data");
          });
        });
      });
      $('#mainCourseDetailsWrapper').on('mouseout', '.courseDetailsTagsList', function()
      {
        $(this).find('.courseTagsDeleteIcon').hide();
      });
      $('#mainCourseDetailsWrapper').on('click', '.courseDetailsTagsList', function()
      {
        var tag_courses_modal = $('#tagCoursesListModal');
        var tagCoursesListBlock = tag_courses_modal.find('#tagCoursesListBlock');
        tagCoursesListBlock.empty();
        var tagCoursesListView
        var tag_id = $(this).attr('data-id');
        var url = ApiUrls.tags + '/' + tag_id;
        var tagCourses = new Apros.collections.TagCourses({ url : url});
        tagCourses.fetch({success: function(){
          tagCoursesListView = new bbGrid.View({
            container: tagCoursesListBlock,
            collection: tagCourses,
            colModel:[
            { title: 'Course Name', index: true, name: 'display_name',
              actions: function(id, attributes){
                var thisId = attributes['course_id']
                var name = attributes['display_name']
                if (name.length > 75){
                  return '<a href="/admin/courses/' + thisId + '" target="_self">' + name.slice(0,75) + '...</a>';
                }
                return '<a href="/admin/courses/' + thisId + '" target="_self">' + name + '</a>';
              }
            },
            { title: 'Course ID', index: true, name: 'course_id' }
          ]});
          tagCoursesListView.render();
          var text = '' + tagCourses.length + ' Courses Tagged with "' + tagCourses.tagDetails + '"';
          tag_courses_modal.find('.tagCoursesListTitle').text(text);
          tag_courses_modal.foundation('reveal', 'open');
        }});
      });
    },
    fetchPages: function(event){
      var _this = event.data.extra;
      if  ($(this).find('.bbGrid-grid.table').height() - $(this).height() - $(this).scrollTop() < 20)
      {
        _this.coursesListDetailsViewGrid.partial_collection.getNextPage();
      }
    },
    onSearchEvent: function(event){
      var _this = event.data.extra;
      if (typeof waitForLastSuccess == 'undefined')
          waitForLastSuccess = true;
        _intervalId = setInterval(function()
        {
          if ($('#courseDetailsMainContainer .bbGrid-pager').val().trim() === '')
            clearInterval(_intervalId)
          waitForLastSuccess = false;
          _this.coursesListDetailsViewGrid.partial_collection.getNextPage({ success: function()
          {
            _this.coursesListDetailsViewGrid.searchBar.onSearch({target: '#courseDetailsMainContainer .bbGrid-pager'});
            waitForLastSuccess = true;
          }});
          if (!_this.coursesListDetailsViewGrid.partial_collection.hasNextPage())
            clearInterval(_intervalId);
      }, 500);
    },
    onClearSearchEvent: function(event){
      var _this = event.data.extra;
      _this.coursesListDetailsViewGrid.searchBar.onSearch({target: '#courseDetailsMainContainer .bbGrid-pager'});
    },
    updateColumns: function(collection, coursesListDetailsViewGrid)
    {
      var assessment_template = { title: '', index: true, name: '', actions: function(id, attributes)
        {
          if (attributes['grade'] == '.')
          {
            return '<i class="fa fa-spinner fa-spin"></i>';
          }
          value = attributes['assessment_final']
          if (value == '-')
            return value;
          return '' + parseInt(value) + '%';
        }};
      var modelsList = collection.models;
      if (modelsList.length > 0)
      {
        for (var i=0; i < modelsList.length; i++)
        {
          if (modelsList[i].attributes.groupworks.length)
          {
            for (var groupworkIndex = 0; groupworkIndex < modelsList[i].attributes.groupworks.length; groupworkIndex++)
            {
              groupworkData = modelsList[i].attributes.groupworks[groupworkIndex];
              groupwork = _.clone(assessment_template);
              groupwork.title = 'Group Work: ' + groupworkData.label;
              groupwork.name = 'groupworks.' + groupworkIndex + '.percent';
              groupwork.actions = (function(groupworkIndex){ return function(id, attributes)
              {
                if (attributes.groupworks.length != attributes.number_of_groupworks)
                {
                  return '<i class="fa fa-exclamation-triangle"></i>'
                }
                if(attributes.groupworks.length == 0){
                  return '' + parseInt('000') + '%';
                }
                var value = attributes.groupworks[groupworkIndex].percent;
                if (value == '.')
                {
                  return '<i class="fa fa-spinner fa-spin"></i>';
                }
                if (value == '-')
                  return value;
                return '' + parseInt(value) + '%';
              }})(groupworkIndex);
              this.generatedGridColumns.push(groupwork);
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
              assessment = _.clone(assessment_template);
              assessment.title = 'Assessment: ' + assessmentData.label;
              assessment.name = 'assessments.' + assessmentIndex + '.percent';
              assessment.actions = (function(assessmentIndex){ return function(id, attributes)
              {
                if (attributes.assessments.length != attributes.number_of_assessments)
                {
                  return '<i class="fa fa-exclamation-triangle"></i>'
                }
                if(attributes.assessments.length == 0){
                  return '' + parseInt('000') + '%';
                }
                var value = attributes.assessments[assessmentIndex].percent;
                if (value == '.')
                {
                  return '<i class="fa fa-spinner fa-spin"></i>';
                }
                if (value == '-')
                  return value;
                return '' + parseInt(value) + '%';
              }})(assessmentIndex);
              this.generatedGridColumns.push(assessment);
            }
            break;
          }
        }
      }
      coursesListDetailsViewGrid.render();
    },
    csvDownloadStatus: function functionName(url, status_element, task_id, _this, _data) {
      $(status_element).parent().find('.loadingIcon').removeClass('hidden');
      var interval_id = setInterval(function(){
        var options = {
            url: url,
            data: {'task_id':task_id},
            type: "GET"
        };
        options.headers = { 'X-CSRFToken': $.cookie('apros_csrftoken')};
        $.ajax(options)
        .done(function(data, textStatus, xhr) {
          if (xhr.status === 200)
          {
            $(status_element).text('Progress: '+ data['values'].progress + '%');
            if (data['values'].completed == 1)
            {
              $(status_element).parent().find('.loadingIcon').addClass('hidden');
              clearInterval(interval_id);

              _this.csvDownloadCallback(_this, _data);
            }
            if (data['error_list'].length > 0)
            {
              console.log(data['error_list']);
            }
          }
        })
        .fail(function(data) {
          console.log("Ajax failed to fetch data");
          console.log(data);
          });
      }, 3000);
      return interval_id;
    },
    realtimeStatus: function(url, status_element, task_id, _this, _data)
    {
      $(status_element).parent().find('.loadingIcon').removeClass('hidden')
      var interval_id = setInterval(function(){
        var options = {
            url: url,
            data: JSON.stringify({'type': 'status_check', 'task_id':task_id}),
            processData: false,
            type: "POST",
            dataType: "json"
          };
        options.headers = { 'X-CSRFToken': $.cookie('apros_csrftoken')};
        $.ajax(options)
        .done(function(data) {
          if (data['status'] == 'ok')
          {
            $(status_element).text('Selected: '+data['values'].selected+', Successful: '+data['values'].successful+', Failed: '+data['values'].failed);
            if (data['values'].successful + data['values'].failed >= data['values'].selected)
            {
              $(status_element).parent().find('.loadingIcon').addClass('hidden');
              clearInterval(interval_id);
              if ((data['values'].failed <= 0) && (data['values'].selected > 0) && (data['values'].selected === data['values'].successful))
              {
                if(_data){
                  _this.createConfirmationScreenOnCourseDetails(_this, _data);
                }
                else {
                  location.reload();
                }
              }
            }
            if (data['error_list'].length > 0)
            {
              console.log(data['error_list']);
            }
          }
        })
        .fail(function(data) {
          console.log("Ajax failed to fetch data");
          console.log(data);
          });
      }, 3000);
      return interval_id;
    },
    manageNewTagPopup: function(input, showPopup)
    {
      var value = $(input).val().trim();
      if (showPopup && (value.length > 0))
      {
        var testValue = value.replace(/ /g,'');
        if (/^[a-z0-9]+$/i.test(testValue))
        {
          if (value.length <= 30)
          {
            $('#courseTagsModal').find('.addTagButton').removeClass('disabled');
            $('#courseTagsModal').find('.errorMessage').empty();
            $(input).parent().find('.newTagCreationPopup').show();
          }
          else
          {
            $('#courseTagsModal').find('.addTagButton').addClass('disabled');
            $('#courseTagsModal').find('.errorMessage').text('This tag name cannot have more than 30 characters!');
            $(input).parent().find('.newTagCreationPopup').hide();
          }
        }
        else
        {
          $('#courseTagsModal').find('.addTagButton').addClass('disabled');
          $('#courseTagsModal').find('.errorMessage').text('This tag name cannot contain non-alphanumeric characters!');
          $(input).parent().find('.newTagCreationPopup').hide();
        }
      }
      else
      {
        $(input).parent().find('.newTagCreationPopup').hide();
      }
    },
    addTagToCourse: function(tag_id, course_id)
    {
      var data = {"tag_id": tag_id};
      var url = ApiUrls.courses_list + '/' + course_id + '/tags';
      var options = {
        url: url,
        data: data,
        type: "POST",
        dataType: "json"
      };
      options.headers = { 'X-CSRFToken': $.cookie('apros_csrftoken')};
      $.ajax(options)
      .done(function(data) {
        if (data['status'] == 'ok')
        {
          var courseTagsIcon = $('#courseDetailsDataWrapper').find('.courseTagsIcon');
          var newTag = $('<div class="courseDetailsTagsList button small radius"></div>');
          newTag.attr('data-id', data['id']);
          var newTagSpan = $('<span></span>');
          newTagSpan.val(data['name']);
          newTagSpan.text(data['name']);
          newTag.css('margin-right', '5px');
          newTag.append(newTagSpan);
          var deleteTagIcon = $('<i class="fa fa-times courseTagsDeleteIcon"></i>');
          deleteTagIcon.css('padding-left', '5px');
          newTag.append(deleteTagIcon);
          courseTagsIcon.before(newTag);
          $('#courseTagsModal').find('a.close-reveal-modal').trigger('click');
        }
        else if (data['status'] == 'error')
        {
          alert("Couldn't add tag to course!")
          return;
        }
      })
      .fail(function(data) {
        console.log("Ajax failed to fetch data");
      });
    }
  });
