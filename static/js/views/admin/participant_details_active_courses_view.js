  Apros.views.ParticipantDetailsActiveCoursesView = Backbone.View.extend({
    initialize: function(){
      $( ".participantDetailsContent" ).hide();
      $( "#participantDetailsActiveCoursesViewGridLoadingImage" ).show();
      var self = this;
      this.collection.fetch().done(function(){
        $( "#participantDetailsActiveCoursesViewGridLoadingImage" ).hide();
        $( "#participantDetailsActiveCoursesViewGrid" ).show();
        self.render();
      });
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
            return '<a href="/admin/courses/' + thisId + '" target="_self">' + name + '</a>'; 
          } 
        },
        { title: 'Course ID', index: true, name: 'id' },
        { title: 'Program', index: true, name: 'program' },
        { title: 'Progress', index: true, name: 'progress', sorttype: 'string' ,
          actions: function(id, attributes){ 
            var progress = attributes['progress']
            return '' + progress + '%'; 
          } 
        },
        { title: 'Proficiency', index: true, name: 'proficiency'},
        { title: 'Status', index: true, name: 'status' },
        { title: 'Unenroll', index: false, name: 'unenroll'}
        ]
      });
    }
  });