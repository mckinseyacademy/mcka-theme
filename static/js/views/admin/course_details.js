  Apros.views.CourseDetailsView = Backbone.View.extend({
    initialize: function(){
      _this = this;
      this.collection.fetch({success:function(collection, response, options)
        {
          _this.updateColumns();
          collection.getSlowFetchedStatus = true;
          collection.slowFieldsSuccess(collection, response, options);
        }});
    },
    render: function(){
      coursesListDetailsViewGrid = {}
      coursesListDetailsViewGrid['partial_collection'] = this.collection;
      coursesListDetailsViewGrid = new bbGrid.View({
        container: this.$el,
        multiselect: true,
        enableSearch: true,
        collection: this.collection.fullCollection,
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
      this.$el.scroll(this.fetchPages);
      $(document).on('onSearchEvent', this.onSearchEvent);
      $(document).on('onClearSearchEvent', this.onClearSearchEvent);
    },
    fetchPages: function(){
      if  (($(this).find('.bbGrid-container').height() - $(this).height() - $(this).scrollTop() < 20) && coursesListDetailsViewGrid.partial_collection.hasNextPage()){
        _collection = coursesListDetailsViewGrid.partial_collection;
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
    onSearchEvent: function(){
    if (typeof waitForLastSuccess == 'undefined')
      waitForLastSuccess = true;
      _intervalId = setInterval(function()
      {
        if ($('#courseDetailsMainContainer .bbGrid-pager').val().trim() === '')
          clearInterval(_intervalId)
        if (waitForLastSuccess)
        {
          waitForLastSuccess = false;
          _collection = coursesListDetailsViewGrid.partial_collection;
          _collection.saveCurrentPageSlowState();
          _collection.getNextPage({success:function(collection, response, options){
            if (!_collection.getSlowFetchedStatus)
            {
              _collection.getSlowFetchedStatus = true;
              _collection.slowFieldsSuccess(_collection, response, options);
            }
            coursesListDetailsViewGrid.searchBar.onSearch({target: '#courseDetailsMainContainer .bbGrid-pager'});
            waitForLastSuccess = true;
          }});
        }
        if (!coursesListDetailsViewGrid.partial_collection.hasNextPage())
          clearInterval(_intervalId);
      }, 500);
    },
    onClearSearchEvent: function(){
      coursesListDetailsViewGrid.searchBar.onSearch({target: '#courseDetailsMainContainer .bbGrid-pager'});
    },
    updateColumns: function(callerType)
    {
      var assessment_midterm = { title: 'Midterm Assessment', index: true, name: 'assessment_midterm', actions: function(id, attributes) 
        { 
          if (attributes['assessment_midterm'] == '.')
          {
            return '<i class="fa fa-spinner fa-spin"></i>';
          }
          value = attributes['assessment_midterm']
          if (value == '-')
            return value;
          return '' + parseInt(value) + '%'; 
        }};
      var assessment_final = { title: 'Final Assessment', index: true, name: 'assessment_final', actions: function(id, attributes) 
        { 
          if (attributes['assessment_final'] == '.')
          {
            return '<i class="fa fa-spinner fa-spin"></i>';
          }
          value = attributes['assessment_final']
          if (value == '-')
            return value;
          return '' + parseInt(value) + '%'; 
        }};
      var group_work = { title: 'Group Work', index: true, name: 'group_work', actions: function(id, attributes) 
        { 
          if (attributes['group_work'] == '.')
          {
            return '<i class="fa fa-spinner fa-spin"></i>';
          }
          value = attributes['group_work']
          if (value == '-')
            return value;
          return '' + parseInt(value) + '%'; 
        }};
      var modelsList = this.collection.fullCollection.models;
      if (modelsList.length > 0)
      {
        if (modelsList[0].attributes['number_of_groupworks'] === 1)
          coursesListDetailsViewGrid.colModel.push(group_work);

        if (modelsList[0].attributes['number_of_assessments'] > 1)
        {
          coursesListDetailsViewGrid.colModel.push(assessment_midterm);
          coursesListDetailsViewGrid.colModel.push(assessment_final); 
        }
        
        if (modelsList[0].attributes['number_of_assessments'] === 1)
          coursesListDetailsViewGrid.colModel.push(assessment_final);
      }
      coursesListDetailsViewGrid.render();
    }
  });