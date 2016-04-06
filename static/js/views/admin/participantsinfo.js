Apros.views.ParticipantsInfo = Backbone.View.extend({
	initialize: function(){
		this.collection.fetch({success: function() {
      cloneHeader('#participantsListViewGridBlock');
    }});
    Dropzone.options.participantsCsvUpload = {
      paramName: 'student_list',
      headers: { 'X-CSRFToken': $.cookie('apros_csrftoken')},
      autoProcessQueue: false,
      init: function() {
        var _this = this;
        var student_list = $("#id_student_list");
        $('#participantsCsvSubmitButton').on('click', function() {
          if($(this).hasClass('disabled'))
            return;
          var fileList = _this.getQueuedFiles().length;
          if (fileList > 0){
            _this.processQueue();
          }
          else if (document.getElementById("id_student_list").files.length > 0) {
            document.getElementById('participantsCsvForm').submit();
          }
        });
        _this.on('addedfile', function() {
          $('#participantsCsvSubmitButton').removeClass('disabled');
        });
        _this.on('removedfile', function() {
          if (student_list[0].files.length = 0) {
            $('#participantsCsvSubmitButton').addClass('disabled');
          }
        });
        student_list.on('change', function() {
          if (student_list[0].files.length > 0) {
            $('#participantsCsvSubmitButton').removeClass('disabled');
          }
          else if(student_list[0].files.length = 0){
            if (_this.getQueuedFiles().length = 0) {
              $('#participantsCsvSubmitButton').addClass('disabled');
            }
          }
        });
      }
    };
	},
	render: function(){
		participantsListViewGrid = new bbGrid.View({
			container: this.$el,
			collection: this.collection.fullCollection,
			colModel:[
				{ title: 'Name', index: true, name: 'full_name', 
				actions: function(id, attributes) 
				{ 
					return '<a href="/admin/participants/' + attributes['id'] + '" target="_self">' + attributes['full_name'] + '</a>';
				}},
				{ title: 'Company', index: true, name: 'organizations_custom_name' },
				{ title: 'Email', index: true, name: 'email' },
				{ title: 'Date Added', index: true, name: 'created_custom_date',
				actions: function(id, attributes) 
				{ 
					if (attributes['created_custom_date'] != '-')
					{
						var start = attributes['created_custom_date'].split('/');
						return '' + start[1] + '/' + start[2] + '/' + start[0];
					}
					return attributes['created_custom_date'];
				}},
				{ title: 'Activated', index: true, name: 'active_custom_text' }]
			});
		participantsListViewGrid['partial_collection']=this.collection;
		this.$el.find('.bbGrid-container').scroll(this.fetchPages);
	},
	fetchPages: function(){
		if  ($(this).find('.bbGrid-grid.table').height() - $(this).height() - $(this).scrollTop() < 20)
		{
			participantsListViewGrid.partial_collection.getNextPage();
		}
	}
});