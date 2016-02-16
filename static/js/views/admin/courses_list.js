  Apros.views.CoursesListView = Backbone.View.extend({
    initialize: function(){
      this.collection.fetch();
    },
    render: function(){
      coursesListViewGrid = new bbGrid.View({
        container: this.$el,
        collection: this.collection.fullCollection,
        colModel:[
        { title: 'Course Name', index: true, name: 'name', sorttype: 'string',
          actions: function(id, attributes){ 
            var thisId = attributes['id']
            var name = attributes['name']
            return '<a href="/admin/course-meta-content/items/' + thisId + '" target="_self">' + name + '</a>'; 
          } 
        },
        { title: 'Course ID', index: true, name: 'id' },
        { title: 'Program', index: true, name: 'program' },
        { title: 'Type', index: true, name: 'type' },
        { title: 'Configuration', index: true, name: 'configuration' },
        { title: 'Start', index: true, name: 'start',
          actions: function(id, attributes){ 
            if (attributes['start'] != '-'){
              var start = attributes['start'].split('/');
              return '' + start[1] + '/' + start[2] + '/' + start[0];
            }
            return attributes['start'];
          } 
        },
        { title: 'End', index: true, name: 'end',
          actions: function(id, attributes){ 
            if (attributes['end'] != '-'){
              var end = attributes['end'].split('/');
              return '' + end[1] + '/' + end[2] + '/' + end[0];
            }
            return attributes['end'];
          } 
        }
        ]
      });
      coursesListViewGrid['partial_collection'] = this.collection;
      this.$el.scroll(this.fetchPages);
    },
    fetchPages: function(){
      if  ($(this).scrollTop() == $(this).find('.bbGrid-container').height() - $(this).height()){
        coursesListViewGrid.partial_collection.getNextPage();
      }
    }
  });