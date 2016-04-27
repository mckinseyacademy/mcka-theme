Apros.views.ParticipantsInfo = Backbone.View.extend({
	initialize: function(){
		this.collection.fetch({success: function() {
      cloneHeader('#participantsListViewGridBlock');
    }});
    massParticipantsInit();
    this.renderAddSingleUser();
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
    $(document).on('closed.fndtn.reveal', '#import_from_csv[data-reveal]', function () {
      $('.upload_stats').empty();
      $('#enroll-error-list').empty();
    });
	},
	fetchPages: function(){
		if  ($(this).find('.bbGrid-grid.table').height() - $(this).height() - $(this).scrollTop() < 20)
		{
			participantsListViewGrid.partial_collection.getNextPage();
		}
	},
	renderAddSingleUser: function()
	{
		var adminAnotherCompanyTemplate = '<div class="row adminAnotherCompany">'+
		  '<div class="large-6 columns participantAdminCompany">'+
		    '<div class="participantAdminCompanyLabel labelUniversal">'+
		      'Admin Company'+
		    '</div>'+
		    '<div class="participantAdminCompanyValue">'+
		      '<input type="text" data-id/>'+
		      '<i class="fa fa-check-circle-o correctInput" aria-hidden="true"></i>'+
		    '</div>'+
		  '</div>'+
		  '<div class="large-6 columns participantPermissions">'+
		    '<div class="participantPermissionsLabel labelUniversal">'+
		      'Admin Permissions'+
		    '</div>'+
		    '<div class="participantPermissionsValue permissionSelect large-10">'+
		      // '<select>'+
		      //   '<option value="uber_admin">Uber admin</option>'+
		      //   '<option value="course_ops_admin">Course ops admin</option>'+
		      //   '<option value="company_admin">Company admin</option>'+
		      //   '<option value="internal_admin">Internal Admin</option>'+
		      // '</select>'+
		      '<input type="text" value="Company Admin" disabled data-id="company_admin"/>'+
		    '</div>'+
		    '<i class="fa fa-times removeItem large-2" aria-hidden="true"></i>'+
		  '</div>'+
		'</div>';
		var enrollInCourseTemplate = '<div class="row enrollInCourse">'+
		  '<div class="large-6 columns participantCourse">'+
		    '<div class="participantCourseLabel labelUniversal">'+
		      'Course'+
		    '</div>'+
		    '<div class="participantCourseValue">'+
		      '<input type="text" data-id/>'+
		      '<i class="fa fa-check-circle-o correctInput" aria-hidden="true"></i>'+
		    '</div>'+
		  '</div>'+
		  '<div class="large-6 columns participantCoursePermissions">'+
		    '<div class="participantCoursePermissionsLabel labelUniversal">'+
		      'Status'+
		    '</div>'+
		    '<div class="participantCoursePermissionsValue permissionSelect large-10">'+
		      '<select>'+
		        '<option value="active">Active</option>'+
		        '<option value="assistant">TA</option>'+
		        '<option value="observer">Observer</option>'+
		      '</select>'+
		    '</div>'+
		    '<i class="fa fa-times removeItem large-2" aria-hidden="true"></i>'+
		  '</div>'+		  	
		'</div>';
		$('#country_edit').countrySelect();
		GetAutocompleteSource(ApiUrls.participant_organization_get_api(), this, 'organization_source');
		GetAutocompleteSource(ApiUrls.participant_courses_get_api(), this, 'course_source');
		var _this = this;
		$('#participantsAddWrapper').find('.participantAddButton').on('click',function()
		{
			if (_this.organization_source)
				GenerateAutocompleteInput(_this.organization_source, '#add_a_participant .participantCompanyValue input');
			else
				InitializeAutocompleteInput(ApiUrls.participant_organization_get_api(), '#add_a_participant .participantCompanyValue input');
			var mainContainer = $('#add_a_participant');
			mainContainer.foundation('reveal', 'open');
			$("#country_edit").countrySelect("selectCountry", 'us');
			mainContainer.find('.adminAnotherCompanyAllWrapper').empty();
			mainContainer.find('.adminCourseAllWrapper').empty();
	  		mainContainer.find('.errorContainer').empty();
	  		mainContainer.find('.cleanable').each(function(i,v){
	  			$(v).val('');
	  			$(v).attr('data-id','');
	  		});
	  		mainContainer.find('.participantEmail .checkMark').hide();
	  		mainContainer.find('.correctInput').hide();
	  		mainContainer.find('.emailActivationLinkCheckboxWrapper').find('input').attr('checked', false);
	  		mainContainer.find('select').each(function(i,v){
	  			$(v).find('option:eq(0)').prop('selected', true);
	  		});
		});
		$('#add_a_participant').find('.addAnotherCompanyWrapper a').on('click', function(event)
		{
			event.preventDefault();
			var objectContainer = $('#add_a_participant').find('.adminAnotherCompanyAllWrapper');
			objectContainer.append(adminAnotherCompanyTemplate);
			var appendedChild = objectContainer.children().last().find('.participantAdminCompanyValue input');
			if (_this.organization_source)
				GenerateAutocompleteInput(_this.organization_source, appendedChild);
			else
				InitializeAutocompleteInput(ApiUrls.participant_organization_get_api(), appendedChild);
		});
		$('#add_a_participant').find('.addAnotherCourseWrapper a').on('click', function(event)
		{
			event.preventDefault();
			var objectContainer = $('#add_a_participant').find('.adminCourseAllWrapper');
			objectContainer.append(enrollInCourseTemplate);
			var appendedChild = objectContainer.children().last().find('.participantCourseValue input');
			if (_this.course_source)
				GenerateAutocompleteInput(_this.course_source, appendedChild);
			else
				InitializeAutocompleteInput(ApiUrls.participant_courses_get_api(), appendedChild);
		});
		$('#add_a_participant').on('click', '.removeItem', function()
		{
			$(this).parents('.row').remove();
		})
		$('#add_a_participant').find('.addSingleParticipantButton').on("click", function()
		{
			if (!$(this).hasClass('disabled'))
			{
				var mainContainer = $('#add_a_participant');
				var data = {}
		        $.each($("#add_a_participant form").find(':input'), function(i, v){
		            var input = $(v);
		            if (input.val())
		                data[input.attr("name")] = input.val().trim();
		            if (input.attr("name") == 'company')
		                data[input.attr("name")] = input.attr('data-id');
		        });

		        $.each($("#add_a_participant form").find('select'), function(i, v){
		            var input = $(v);
		            if (input.val())
		                data[input.attr("name")] = input.val().trim();   
		        });

		        delete data["undefined"];
		        data['course_permissions_list'] = _this.getAllCourses();
		        data['send_activation_email'] = mainContainer.find('.emailActivationLinkCheckboxWrapper').find('input').is(":checked");

		        $.ajax({
		        type: 'POST',
		        url: '/admin/api/participants',
		        headers: { 'X-CSRFToken': $.cookie('apros_csrftoken')},
		        contentType: 'application/json; charset=utf-8',
		        data: JSON.stringify(data),
		        dataType: 'text',
		        cache: false,
		        success: function (data, status) 
		        {
					data = JSON.parse(data)
			        if (data['status'] == "ok") 
			        {
						var confirmationScreen = $('#confirmation_screen_single_participant');
						confirmationScreen.find('.download_user_activation').attr('href', confirmationScreen.find('.download_user_activation').attr('data-url') + data['user_id']);
						confirmationScreen.find('.go_to_user_profile').attr('href', confirmationScreen.find('.go_to_user_profile').attr('data-url') + data['user_id']);
						confirmationScreen.foundation('reveal', 'open');
			        }
			        else 
			        {
						if (data['type'] == 'validation_failed')
						{
							var message = '';
							for (key in data['message'])
							{
								message += key + ' - ' + data['message'][key] + '<br>';
							}
							$('#add_a_participant').find('.errorContainer').html(message);
						}
						else
						{
							$('#add_a_participant').find('.errorContainer').text(data['message']);
						}
					}
		        },
		        error: function(data, status)
		        {
		          $('#add_a_participant').find('.errorContainer').text(data['responseText']);
		        }
		        });
        	}
      	}); 
        
    },
    getAllCourses: function()
    {
      var courseContainer = $('#add_a_participant').find('.adminCourseAllWrapper');
      var courseArray = [];
      courseContainer.find('.row').each(function()
      {
        var course = $(this);
        var courseObject = {};
        var courseId = course.find('input').attr('data-id');
        if (courseId != '')
        {
          courseObject['course_id'] = courseId;
          courseObject['role'] = course.find('select').val();
          courseArray.push(courseObject);
        }
      });
      return courseArray;
    }
});