  Apros.views.CourseDetailsView = Backbone.View.extend({

    coursesListDetailsViewGrid: {},
    generatedGridColumns:
    [
      { title: gettext('Name'), index: true, name: 'custom_full_name', titleAttribute: 'custom_full_name',
      actions: function(id, attributes)
      {
        var companyPageFlag = $('#courseDetailsDataWrapper').attr('company-page');

        if (companyPageFlag == 'False')
        {
          return '<a href="/admin/participants/' + attributes['id'] + '" target="_self">' + attributes['custom_full_name'] + '</a>';
        }
        else
        {
          var companyAdminFlag = $('#courseDetailsDataWrapper').attr('admin-flag');
          if (companyAdminFlag == 'False')
          {
            return '<a href="/admin/participants/' + attributes['id'] + '" target="_self">' + attributes['custom_full_name'] + '</a>';
          }
          else
          {
              return attributes['custom_full_name']
          }
        }
      }},
      { title: gettext('Email'), index: true, name: 'email' },
      { title: gettext('Company'), index: true, name: 'organizations_display_name'},
      { title: gettext('Status'), index: true, name: 'custom_user_status'},
      { title: gettext('Activated'), index: true, name: 'custom_activated'},
      { title: gettext('Cohort'), index: true, name: 'course_groups',
      actions: function(id, attributes)
      {
        if (attributes['course_groups'].length > 0) {
          return attributes['course_groups'][0];
        }
        return '-';
      }},
      { title: gettext('Last Log In'), index: true, name: 'custom_last_login',
      actions: function(id, attributes)
      {
        if (attributes['custom_last_login'] != '-' && attributes['custom_last_login'] != '' && typeof attributes['custom_last_login'] != 'undefined')
        {
         // Todo: need to define dateformat from server side for internationalization
         var last_login = attributes['custom_last_login'].split(',')[0].split('/');
            return '' + last_login[1] + '/' + last_login[2] + '/' + last_login[0];
        }
        return attributes['custom_last_login'];
      }},
      { title: gettext('Progress'), index: true, name: 'progress', actions: function(id, attributes)
      {
        value = attributes['progress'];
        if (value == '-')
          return value;
        return InternationalizePercentage(parseInt(value));
      }},
      { title: gettext('Proficiency'), index: true, name: 'proficiency', actions: function(id, attributes)
      {
        value = attributes['proficiency'];
        if (value == '-')
          return value;
        return parseInt(value);
      }},
      { title: gettext('Engagement'), index: true, name: 'engagement', actions: function(id, attributes)
      {
        value = attributes['engagement'];
        if (value == '-')
          return value;
        return '' + parseInt(value);
      }},
      { title: gettext('Activation Link'), index: true, name: 'activation_link', actions: function (id, attributes) {
        var value = attributes['activation_link'];

        if(value != '')
            value = '<a href="' + value + '">' + gettext('Activation Link') + '</a>';

        return value;
      }},
      { title: gettext('Username'), index: true, name: 'username' },
      { title: gettext('Country'), index: true, name: 'country'}
    ],
    initialize: function(options){
      if (typeof options['participantscollection'] !== "undefined") {
        this.participantscollection = options['participantscollection'];
      }
      InitializeTooltipOnPage();
      var _this = this;
      var companyPageFlag = $('#courseDetailsDataWrapper').attr('company-page');
      if (companyPageFlag == 'True')
      {
        var companyId = $('#courseDetailsDataWrapper').attr('company-id');
        this.collection.updateCompanyQuerryParams(companyId);
      }
      try {
        var count = course_details_count_all_users;
        this.cohorts_enabled = course_details_cohorts_enabled;
        this.cohorts_available = course_details_cohorts_available;
      }
      catch(error) {
        var count = '0';
      }
      finally {
        this.collection.updateCountQuerryParams(count);
        this.collection.fetch();
      }
    },
    removeFromGeneratedGridColumns: function(title){
      var _this = this;
      var index = 0;
      for (var i=0; i < _this.generatedGridColumns.length; i++ )
      {
        if (_this.generatedGridColumns[i]['title'] == gettext(title))
        {
          index = i;
        }
      }
      _this.generatedGridColumns.splice(index, 1);
    },
    render: function(){
      var _this = this;
      var companyAdminFlag = $('#courseDetailsDataWrapper').attr('admin-flag');
      var courseId = $('#courseDetailsDataWrapper').attr('data-id');
      var multiSelectFlag = true;
      if (companyAdminFlag == 'True')
      {
        _this.removeFromGeneratedGridColumns('Company');
      }
      if (this.cohorts_enabled == 'False' || this.cohorts_available == 'False') {
        _this.removeFromGeneratedGridColumns('Cohort');
      }
      var coursesListDetailsViewGrid = {};
      coursesListDetailsViewGrid['partial_collection'] = this.collection;
      coursesListDetailsViewGrid = new bbGrid.View({
        container: this.$el,
        multiselect: multiSelectFlag,
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
      $('.bbGrid-container').append('<i class="fa fa-spinner fa-spin"></i>');
      coursesListDetailsViewGrid['partial_collection'] = this.collection;
      this.coursesListDetailsViewGrid = coursesListDetailsViewGrid;
      this.$el.find('.bbGrid-container').on('scroll', { extra : this}, this.fetchPages);
      var _pointer = this;
      _pointer.course_participant_search_flag = true;
      _pointer.default_first_page = true;
      $(document).on('onSearchEvent', { extra : this}, this.onSearchEvent);
      $(document).on('onClearSearchEvent', { extra : this}, this.onClearSearchEvent);

      $('#courseDetailsParticipantsGridWrapper .bbGrid-search-bar, #courseDetailsParticipantsSearchWrapper.bbGrid-search-bar').on('enter', 'input', function(event, status){
          if (_pointer.course_participant_search_flag) {
              _pointer.course_participant_search_flag = false;
              var querryDict = {};
              var searchFlag = false;
              var course_id = $('#courseDetailsDataWrapper').attr('data-id');
              if (status.clearButton){
                var value = '';
              }else{
                  var value = $('#courseDetailsParticipantsGridWrapper .bbGrid-search-bar, #courseDetailsParticipantsSearchWrapper.bbGrid-search-bar').find('input').val().trim();
              }
              var companyPageFlag = $('#courseDetailsDataWrapper').attr('company-page');
              if (companyPageFlag == 'True')
              {
                var company_id = $('#courseDetailsDataWrapper').attr('company-id');
                querryDict['organizations'] = company_id;
              }
              querryDict['search_query_string'] = value;
              querryDict['courses'] = course_id;
              querryDict['course_id'] = course_id;
              querryDict['course_participants_search'] = 'course_participants_search';
              if (value) {
                  searchFlag = true
              }
              if (!jQuery.isEmptyObject(querryDict)) {
                  _pointer.participantscollection.updateQuerryParams(querryDict);
                  if (!_pointer.participantscollection.queryParams['search_query_string']){
                    _pointer.participantscollection.queryParams['search_query_string'] = value;
                  }
              }
              if ((_pointer.participantscollection.length > 0 && searchFlag) || (status.clearButton && !_pointer.default_first_page)) {
                  _pointer.participantscollection.getFirstPage();
                  _pointer.participantscollection.fullCollection.reset();
                  $('i.fa-spinner').show();
              }
              if ((searchFlag) || (status.clearButton && !_pointer.default_first_page)) {
                  $.when(_pointer.participantscollection.fetch()).then(function() {
                  $('i.fa-spinner').hide();
                  _pointer.coursesListDetailsViewGrid.setCollection(_pointer.participantscollection.fullCollection);
                  _pointer.coursesListDetailsViewGrid.collection.trigger('reset');
                  _pointer.coursesListDetailsViewGrid.partial_collection = _pointer.participantscollection;
                  _pointer.course_participant_search_flag = true;
                  if (searchFlag){
                    _pointer.default_first_page = false;
                  } else {
                    _pointer.default_first_page = true;
                  }
                  });
              }
              else{
                _pointer.course_participant_search_flag = true;
              }
          }
      });

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
              // Todo: Internationalization: decide how we can handle internal in other language
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
                  alert(gettext("Couldn't create new tag!"))
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
              $('#courseTagsModal').find('.errorMessage').text(gettext("You don't have permission to create a new tag, please select one from the list!"));
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
              alert(gettext("Couldn't delete tag!"))
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
            { title: gettext('Course Name'), index: true, name: 'display_name',
              actions: function(id, attributes){
                var thisId = attributes['course_id']
                var name = attributes['display_name']
                if (name.length > 75){
                  return '<a href="/admin/courses/' + thisId + '" target="_self">' + name.slice(0,75) + '...</a>';
                }
                return '<a href="/admin/courses/' + thisId + '" target="_self">' + name + '</a>';
              }
            },
            { title: gettext('Course ID'), index: true, name: 'course_id' }
          ]});
          tagCoursesListView.render();
          var text = ngettext('%(count)s Course Tagged with %(tagDetails)s',
              '%(count)s Courses Tagged with %(tagDetails)s', tagCourses.length);
          var tagDetails = {
            'count': tagCourses.length,
            'tagDetails': tagCourses.tagDetails
          };

          tag_courses_modal.find('.tagCoursesListTitle').text(interpolate(text, tagDetails, true));
          tag_courses_modal.foundation('reveal', 'open');
        }});
      });
    },
    fetchPages: function(event){
      var _this = event.data.extra;
      if  ($(this).find('.bbGrid-grid.table').height() - $(this).height() - $(this).scrollTop() < 20)
      {
        $(this).find('i.fa-spinner').show();
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
            if (data['values'].state != 'RETRY')
                var status_message = gettext('Progress: %(progress)s %')
                var progress_status = {'progress': data['values'].progress}
              $(status_element).text(interpolate(status_message, progress_status, true));

            if (data['values'].state == 'SUCCESS' || data['values'].state == 'FAILURE')
            {
              $(status_element).parent().find('.loadingIcon').addClass('hidden');
              clearInterval(interval_id);

              _this.csvDownloadCallback(_this, data);
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
            contentType: "application/json; charset=utf-8",
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
            var status_message = gettext('Selected: %(selected)s, Successful: %(successful)s, Failed: %(failed)s');
            var message_context = {
              'selected': data['values'].selected,
              'successful': data['values'].successful,
              'failed': data['values'].failed
            };
            $(status_element).text(interpolate(status_message, message_context, true));
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
            $('#courseTagsModal').find('.errorMessage').text(gettext('This tag name cannot have more than 30 characters!'));
            $(input).parent().find('.newTagCreationPopup').hide();
          }
        }
        else
        {
          $('#courseTagsModal').find('.addTagButton').addClass('disabled');
          $('#courseTagsModal').find('.errorMessage').text(gettext('This tag name cannot contain non-alphanumeric characters!'));
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
          alert(gettext("Couldn't add tag to course!"))
          return;
        }
      })
      .fail(function(data) {
        console.log("Ajax failed to fetch data");
      });
    }
  });

$(function() {
    $('#courseDetailsParticipantsGridWrapper .bbGrid-search-bar, #courseDetailsParticipantsSearchWrapper.bbGrid-search-bar').find('input').keyup(function(e){
      if(e.keyCode == 13){
        $(this).trigger('enter', [{ clearButton : false}]);
      }
    });

    $('#courseDetailsParticipantsGridWrapper .bbGrid-search-bar, #courseDetailsParticipantsSearchWrapper.bbGrid-search-bar').find('input').courseParticipantsclearSearch({ callback: function() {
          $('#courseDetailsParticipantsGridWrapper .bbGrid-search-bar, #courseDetailsParticipantsSearchWrapper.bbGrid-search-bar').find('input').trigger('enter', [{ clearButton : true}]);
    } } );

    // update value
    $('#courseDetailsParticipantsGridWrapper .bbGrid-search-bar, #courseDetailsParticipantsSearchWrapper.bbGrid-search-bar').find('input').val('').change();
});

  (function ($) {
    $.fn.courseParticipantsclearSearch = function (options) {
      var settings = $.extend({
        'clearClass': 'clear_input',
        'focusAfterClear': true,
        'linkText': '&times;'
      }, options);
      return this.each(function () {
        var $this = $(this), btn,
            divClass = settings.clearClass + '_div';

        if (!$this.parent().hasClass(divClass)) {
          $this.wrap('<div style="position: relative;" class="'
              + divClass + '">' + $this.html() + '</div>');
          $this.after('<a style="position: absolute; cursor: pointer;" class="'
              + settings.clearClass + '">' + settings.linkText + '</a>');
        }
        btn = $this.next();

        function clearField() {
          $this.val('').change();
          triggerBtn();
          if (settings.focusAfterClear) {
            $this.focus();
          }
          if (typeof (settings.callback) === "function") {
            settings.callback();
          }
        }

        function blankField() {
          triggerBtn();
          if (!hasText()) {
            if ($this.liveSearchTimer) {
              clearTimeout($this.liveSearchTimer);
            }

            $this.liveSearchTimer = setTimeout(function () {
              if (typeof (settings.callback) === "function") {
                settings.callback();
              }
            }, 1000)
          }
        }

        function triggerBtn() {
          if (hasText()) {
            btn.show();
          } else {
            btn.hide();
          }
          update();
        }

        function hasText() {
          return $this.val().length > 0;
        }

        function update() {
          var width = $this.outerWidth(), height = $this
              .outerHeight();
          btn.css({
            top: height / 2 - btn.height() / 2,
            left: width - height / 2 - btn.height() / 2
          });
        }

        btn.on('click', clearField);
        $this.on('keyup', blankField);
        triggerBtn();
      });
    };
  })(jQuery);
