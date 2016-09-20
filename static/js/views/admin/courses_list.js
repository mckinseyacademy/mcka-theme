  Apros.views.CoursesListView = Backbone.View.extend({
    initialize: function(){
      this.collection.fetch({success: function(){
        cloneHeader('#coursesListViewGridBlock');
      }});
    },
    render: function(){
      coursesListViewGrid = new bbGrid.View({
        enableSearch: true,
        container: this.$el,
        collection: this.collection.fullCollection,
        colModel:[
        { title: 'Course Name', index: true, name: 'name', sorttype: 'string',
          actions: function(id, attributes){ 
            var thisId = attributes['id'];
            var name = attributes['name'];
            if (name.length > 75){
              return '<a href="/admin/courses/' + thisId + '" target="_self">' + name.slice(0,75) + '...</a>'; 
            }
            return '<a href="/admin/courses/' + thisId + '" target="_self">' + name + '</a>'; 
          } 
        },
        { title: 'Course ID', index: true, name: 'id' },
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
      $(document).on('onClearSearchEvent', this.onClearSearchEvent);

    },
    onClearSearchEvent: function(){
      coursesListViewGrid.searchBar.onSearch({target: '#mainCoursesListBlockContainer .bbGrid-pager'});
    }
  });