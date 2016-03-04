  Apros.views.ParticipantDetailsActiveCoursesView = Backbone.View.extend({
    initialize: function(){
      this.collection.fetchExtended({success:function(collection, response, options)
        {
          collection.getSlowFetchedStatus = true;
          collection.slowFieldsSuccess(collection, response, options);
        }});
    },
    render: function(){
      participantDetailsActiveCoursesViewGrid = new bbGrid.View({
        container: this.$el,
        collection: this.collection,
        colModel:[
        { title: 'Course Name', index: true, name: 'name', sorttype: 'string',
          actions: function(id, attributes){ 
            var thisId = attributes['id']
            var name = attributes['name']
            if (name)
              return '<a href="/admin/courses/' + thisId + '" target="_self">' + name + '</a>'; 
          } 
        },
        { title: 'Course ID', index: true, name: 'id' },
        { title: 'Program', index: true, name: 'program' },
        { title: 'Progress', index: true, name: 'progress', sorttype: 'string',
          actions: function(id, attributes){ 
            var progress = attributes['progress']
            if (typeof progress != 'undefined') {
              if (progress == '.') {
                return '<i class="fa fa-spinner fa-spin"></i>';
              }
              return '' + progress + '%'; 
            }
          } 
        },
        { title: 'Proficiency', index: true, name: 'proficiency', sorttype: 'string',
          actions: function(id, attributes){ 
            var proficiency = attributes['proficiency']
            if (typeof proficiency != 'undefined') {
              if (proficiency == '.') {
                return '<i class="fa fa-spinner fa-spin"></i>';
              }
              return '' + proficiency; 
            }
          } 
        },
        { title: 'Status', index: true, name: 'status' },
        { title: 'Unenroll', index: false, name: 'unenroll'}
        ]
      });
    }
  });