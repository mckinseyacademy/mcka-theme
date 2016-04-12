  Apros.views.ParticipantDetailsActiveCoursesView = Backbone.View.extend({
    initialize: function(){
      this.collection.fetch({success:function(collection, response, options)
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
              if (progress[0] != '0')
                return '' + progress + '%'; 
              if (progress[1] != '0')
                return '' + progress[1] + progress[2] + '%'; 
              return '' + progress[2] + '%'; 
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
              if (proficiency[0] != '0')
                return '' + proficiency + '%'; 
              if (proficiency[1] != '0')
                return '' + proficiency[1] + proficiency[2] + '%'; 
              return '' + proficiency[2] + '%'; 
            }
          } 
        },
        { title: 'Status', index: true, name: 'status' },
        { title: 'Unenroll', index: false, name: 'unenroll'}
        ]
      });
    }
  });