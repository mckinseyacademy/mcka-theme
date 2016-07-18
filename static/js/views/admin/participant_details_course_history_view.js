  Apros.views.ParticipantDetailsCourseHistoryView = Backbone.View.extend({
    initialize: function(){
      this.collection.fetch();
    },
    render: function(){
      participantDetailsCourseHistoryViewGrid = new bbGrid.View({
        container: this.$el,
        collection: this.collection,
        colModel:[
        { title: 'Course Name', index: true, name: 'name', sorttype: 'string',
          actions: function(id, attributes){ 
            var thisId = attributes['id']
            var name = attributes['name']
            var companyAdminFlag = $('#participantsDetailsDataWrapper').attr('admin-flag');
            if (companyAdminFlag == 'False')
            {
              if (name) {
                return '<a href="/admin/courses/' + thisId + '" target="_self">' + name + '</a>'; 
              }
            }
            else
            {
              var companyId = $('#participantsDetailsDataWrapper').attr('company-id');
              return '<a href="/admin/companies/' +  companyId + '/courses/' + thisId + '" target="_self">' + name + '</a>'; 
            }
          } 
        },
        { title: 'Course ID', index: true, name: 'id' },
        { title: 'Program', index: true, name: 'program' },
        { title: 'Completed', index: true, name: 'completed' },
        { title: 'Grade', index: true, name: 'grade' },
        { title: 'Status', index: true, name: 'status' },
        { title: 'End Date', index: true, name: 'end',
          actions: function(id, attributes){ 
            var end = attributes['end'].split('/');
            return '' + end[1] + '/' + end[2] + '/' + end[0];
          } 
        }
        ]
      });
    }
  });