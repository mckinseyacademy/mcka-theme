  Apros.views.CourseDetailsView = Backbone.View.extend({

    coursesListDetailsViewGrid: {},

    initialize: function(){
      var _this = this;
      this.collection.fetch({success:function(collection, response, options){
          _this.updateColumns(_this.collection, _this.coursesListDetailsViewGrid);
          cloneHeader('#courseDetailsParticipantsGrid');
          collection.getSlowFetchedStatus = true;
          collection.slowFieldsSuccess(collection, response, options);
        }});
    },
    render: function(){
      var coursesListDetailsViewGrid = {}
      coursesListDetailsViewGrid['partial_collection'] = this.collection;
      coursesListDetailsViewGrid = new bbGrid.View({
        container: this.$el,
        multiselect: true,
        enableSearch: true,
        collection: this.collection.fullCollection,
        onRowClick: function()
        {
          console.log('clicked row');
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
        colModel:[
        { title: 'Name', index: true, name: 'username', 
        actions: function(id, attributes) 
        { 
          return '<a href="/admin/participants/' + attributes['id'] + '" target="_self">' + attributes['username'] + '</a>';
        }},
        { title: 'Email', index: true, name: 'email' },
        { title: 'Company', index: true, name: 'organizations_display_name'},
        { title: 'Status', index: true, name: 'custom_user_status',actions: function(id, attributes) 
        { 
          if (attributes['custom_user_status'] == '.')
          {
            return '<i class="fa fa-spinner fa-spin"></i>';
          }
          return attributes['custom_user_status'];
        }},
        { title: 'Activated', index: true, name: 'custom_activated'},
        { title: 'Last Log In', index: true, name: 'custom_last_login',
        actions: function(id, attributes) 
        { 
          if (attributes['custom_last_login'] != '-' && attributes['custom_last_login'] != '' && typeof attributes['custom_last_login'] != 'undefined')
          {
            var start = attributes['custom_last_login'].split('/');
            return '' + start[1] + '/' + start[2] + '/' + start[0];
          }
          return attributes['custom_last_login'];
        }},
        { title: 'Progress', index: true, name: 'progress', actions: function(id, attributes) 
        { 
          if (attributes['progress'] == '.')
          {
            return '<i class="fa fa-spinner fa-spin"></i>';
          }
          value = attributes['progress']
          if (value == '-')
            return value;
          return '' + parseInt(value) + '%'; 
        }},
        { title: 'Proficiency', index: true, name: 'proficiency', actions: function(id, attributes) 
        { 
          if (attributes['proficiency'] == '.')
          {
            return '<i class="fa fa-spinner fa-spin"></i>';
          }
          value = attributes['proficiency']
          if (value == '-')
            return value;
          return '' + parseInt(value) + '%'; 
        }}
        ]
      });
      
      coursesListDetailsViewGrid['partial_collection'] = this.collection;
      this.coursesListDetailsViewGrid = coursesListDetailsViewGrid;
      this.$el.find('.bbGrid-container').on('scroll', { extra : this}, this.fetchPages);
      $(document).on('onSearchEvent', { extra : this}, this.onSearchEvent);
      $(document).on('onClearSearchEvent', { extra : this}, this.onClearSearchEvent);
    },
    fetchPages: function(event){
      var _this = event.data.extra;
      if  (($(this).find('.bbGrid-grid.table').height() - $(this).height() - $(this).scrollTop() < 20) && _this.coursesListDetailsViewGrid.partial_collection.hasNextPage()){
        _collection = _this.coursesListDetailsViewGrid.partial_collection;
        _collection.saveCurrentPageSlowState();
        _collection.getNextPage({success:function(collection, response, options){
          if (!_collection.getSlowFetchedStatus)
          {
            _collection.getSlowFetchedStatus = true;
            _collection.slowFieldsSuccess(_collection, response, options);
          }
        }});
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
        if (waitForLastSuccess)
        {
          waitForLastSuccess = false;
          _collection = _this.coursesListDetailsViewGrid.partial_collection;
          _collection.saveCurrentPageSlowState();
          _collection.getNextPage({success:function(collection, response, options){
            if (!_collection.getSlowFetchedStatus)
            {
              _collection.getSlowFetchedStatus = true;
              _collection.slowFieldsSuccess(_collection, response, options);
            }
            _this.coursesListDetailsViewGrid.searchBar.onSearch({target: '#courseDetailsMainContainer .bbGrid-pager'});
            waitForLastSuccess = true;
          }});
        }
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
        for (var groupworkIndex = 0; groupworkIndex < modelsList[0].attributes.groupworks.length; groupworkIndex++)
        {
          groupworkData = modelsList[0].attributes.groupworks[groupworkIndex];
          groupwork = _.clone(assessment_template);
          groupwork.title = 'Group Work: ' + groupworkData.label;
          groupwork.name = 'groupworks.' + groupworkIndex + '.percent';
          groupwork.actions = (function(groupworkIndex){ return function(id, attributes) 
          { 
            if (attributes.groupworks.length != attributes.number_of_groupworks)
            {
              return '<i class="fa fa-exclamation-triangle"></i>'
            }
            var value = attributes.groupworks[groupworkIndex].percent
            if (value == '.')
            {
              return '<i class="fa fa-spinner fa-spin"></i>';
            }
            if (value == '-')
              return value;
            return '' + parseInt(value) + '%'; 
          }})(groupworkIndex);
          coursesListDetailsViewGrid.colModel.push(groupwork); 
        }
        var assessmentData;
        for (var assessmentIndex = 0; assessmentIndex < modelsList[0].attributes.assessments.length; assessmentIndex++)
        {
          assessmentData = modelsList[0].attributes.assessments[assessmentIndex];
          assessment = _.clone(assessment_template);
          assessment.title = 'Assessment: ' + assessmentData.label;
          assessment.name = 'assessments.' + assessmentIndex + '.percent';
          assessment.actions = (function(assessmentIndex){ return function(id, attributes) 
          { 
            if (attributes.assessments.length != attributes.number_of_assessments)
            {
              return '<i class="fa fa-exclamation-triangle"></i>'
            }
            var value = attributes.assessments[assessmentIndex].percent
            if (value == '.')
            {
              return '<i class="fa fa-spinner fa-spin"></i>';
            }
            if (value == '-')
              return value;
            return '' + parseInt(value) + '%'; 
          }})(assessmentIndex);
          coursesListDetailsViewGrid.colModel.push(assessment); 
        }
      }
      coursesListDetailsViewGrid.render();
    },
    realtimeStatus: function(url, status_element, task_id)
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
                location.reload();
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
      }, 500);
      return interval_id;
    }
  });
