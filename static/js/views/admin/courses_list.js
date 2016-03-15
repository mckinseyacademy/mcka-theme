  Apros.views.CoursesListView = Backbone.View.extend({
    initialize: function(){
      this.collection.fetch();
    },
    render: function(){
      coursesListViewGrid = new bbGrid.View({
        enableSearch: true,
        container: this.$el,
        collection: this.collection.fullCollection,
        colModel:[
        { title: 'Course Name', index: true, name: 'name', sorttype: 'string',
          actions: function(id, attributes){ 
            var thisId = attributes['id']
            var name = attributes['name']
            return '<a href="/admin/courses/' + thisId + '" target="_self">' + name + '</a>'; 
          } 
        },
        { title: 'Course ID', index: true, name: 'id' },
        { title: 'Program', index: true, name: 'program' },
        { title: 'Type', index: true, name: 'type' },
        { title: 'Configuration', index: true, name: 'configuration' },
        { title: 'Start', index: true, name: 'start',
          actions: function(id, attributes){ 
            if (attributes['start'] != '-'){
              var start = attributes['start'].split(',')[0].split('/');
              return '' + start[1] + '/' + start[2] + '/' + start[0];
            }
            return attributes['start'];
          } 
        },
        { title: 'End', index: true, name: 'end',
          actions: function(id, attributes){ 
            if (attributes['end'] != '-'){
              var end = attributes['end'].split(',')[0].split('/');
              return '' + end[1] + '/' + end[2] + '/' + end[0];
            }
            return attributes['end'];
          } 
        }
        ]
      });
      coursesListViewGrid['partial_collection'] = this.collection;
      this.$el.scroll(this.fetchPages);
      $(document).on('onSearchEvent', this.onSearchEvent);
      $(document).on('onClearSearchEvent', this.onClearSearchEvent);

    },
    fetchPages: function(){
        if  ($(this).find('.bbGrid-container').height() - $(this).height() - $(this).scrollTop() < 20)
        {
          coursesListViewGrid.partial_collection.getNextPage();
        }  
    },
    onSearchEvent: function(){
        if (typeof waitForLastSuccess == 'undefined')
          waitForLastSuccess = true;
        _intervalId = setInterval(function()
        {
          if ($('#mainCoursesListBlockContainer .bbGrid-pager').val().trim() === '')
            clearInterval(_intervalId)
          waitForLastSuccess = false;
          coursesListViewGrid.partial_collection.getNextPage({ success: function()
          {
            coursesListViewGrid.searchBar.onSearch({target: '#mainCoursesListBlockContainer .bbGrid-pager'});
            waitForLastSuccess = true;
          }});
          if (!coursesListViewGrid.partial_collection.hasNextPage())
            clearInterval(_intervalId);
        }, 500);
    },
    onClearSearchEvent: function(){
      coursesListViewGrid.searchBar.onSearch({target: '#mainCoursesListBlockContainer .bbGrid-pager'});
    }
  });