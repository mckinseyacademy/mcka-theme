  Apros.views.CourseDetailsView = Backbone.View.extend({
    initialize: function(){
      this.collection.fetch({success:function(collection, response, options)
        {
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
          progress = attributes['progress']
          if (progress[0] != '0')
            return '' + progress + '%'; 
          if (progress[1] != '0')
            return '' + progress[1] + progress[2] + '%'; 
          return '' + progress[2] + '%'; 
        }},
        { title: 'Proficiency', index: true, name: 'proficiency', actions: function(id, attributes) 
        { 
          if (attributes['proficiency'] == '.')
          {
            return '<i class="fa fa-spinner fa-spin"></i>';
          }
          proficiency = attributes['proficiency']
          if (proficiency[0] != '0')
            return '' + proficiency + '%'; 
          if (proficiency[1] != '0')
            return '' + proficiency[1] + proficiency[2] + '%'; 
          return '' + proficiency[2] + '%'; 
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
    }
  });