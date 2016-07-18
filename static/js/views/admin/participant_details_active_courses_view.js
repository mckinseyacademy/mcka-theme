  Apros.views.ParticipantDetailsActiveCoursesView = Backbone.View.extend({
    user_id: null,
    selected_course_id: null,
    participantDetailsActiveCoursesViewGrid: null,

    events: {
      'click .edit-status' : 'editStatus', 
      'click .unenroll-user' : 'unenrollUser', 
      'editStatusDone': 'editStatusHandler'
      }, 

    initialize: function(options){
      if (typeof options['user_id'] !== "undefined") {
        this.user_id = options['user_id'];
      }
      this.refreshCollection();

      var _this = this;

      ajaxify_overlay_form('#edit-status-modal', 'form', 
        function() {
          _this.$el.trigger('editStatusDone');
        }
      );

      $('#unenroll-user-modal .okbutton').on('click', function (e) {
        var url = '/admin/participants/' + _this.user_id + '/courses/' + _this.selected_course_id + '/unenroll';
        $.ajax({
          method: 'GET',
          url: url,
          data: {}
        })
        .done(function(data, status, xhr) { 
          if(data.status == 'success') {
            _this.editStatusHandler();
          }
          else {
            $('#unenroll-user-modal').find('.error').text(data.message);
          }
        });
      });
    },
    refreshCollection: function() {
      this.collection.fetch({success:function(collection, response, options)
        {
          collection.getSlowFetchedStatus = true;
          collection.slowFieldsSuccess(collection, response, options);
        }});
    },
    render: function(){
      var _this = this;
      var gridColumns = 
      [
        { title: 'Course Name', index: true, name: 'name', sorttype: 'string',
          actions: function(id, attributes){ 
            var thisId = attributes['id'];
            var name = attributes['name'];
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
        { title: 'Status', index: true, name: 'status', 
        actions: function(id, attributes) {
            var status = attributes['status'];
            var companyAdminFlag = $('#participantsDetailsDataWrapper').attr('admin-flag');
            if (companyAdminFlag == 'False')
            {
              return status + ' <a class="edit-status fa fa-pencil" data-revealhref="/admin/participants/' + 
              _this.user_id + '/courses/' + id + 
              '/edit_status"></a>';
            }
            else
            {
              return status;
            }
          }
        }
        ];
      var companyAdminFlag = $('#participantsDetailsDataWrapper').attr('admin-flag');
      if (companyAdminFlag == 'False')
      {
        var unerollColumn =  { title: 'Unenroll', index: false, name: 'unenroll',
          actions: function(id, attributes){ 
            return '<a href="#" data-courseid="' + id + '" class="unenroll-user">Unenroll</a>'; 
          } };
        gridColumns.push(unerollColumn);
      }
      this.delegateEvents();
      if(this.participantDetailsActiveCoursesViewGrid) {
        this.participantDetailsActiveCoursesViewGrid.undelegateEvents();
        this.$el.html('');
      }
      this.participantDetailsActiveCoursesViewGrid = new bbGrid.View({
        container: this.$el,
        collection: this.collection,
        colModel: gridColumns
      });
    }, 
    editStatus: function(e) {
      var target = $(e.target);
      var currentRoles = target.parent().text().trim();
      $('#edit-status-modal').foundation('reveal', 'open', {
        url: $(e.target).data('revealhref'),
        data: {currentRoles: currentRoles}
    });
    },
    editStatusHandler: function(e) {
      setTimeout(function(){$('#edit-status-modal').foundation('reveal', 'close')}, 1000);
      this.undelegateEvents();
      this.refreshCollection();
      this.render();
    }, 
    unenrollUser: function(e) {
      var target = $(e.target);
      this.selected_course_id = target.data('courseid');
      $('#unenroll-user-modal').foundation('reveal', 'open');
    }
  });
