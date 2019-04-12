Apros.views.ParticipantsInfo = Backbone.View.extend({
    initialize: function(){
      massParticipantsInit();
      massParticipantsDeleteInit();
      massParticipantsEnrollInit();
      massParticipantsUnenrollInit();
      massParticipantsProfileUpdateInit();
      massParticipantsManagerUpdateInit();
      this.renderAddSingleUser();
      this.userToBeDeleted = null;
    },
    render: function(){
        var _this = this;
        table_columns = [
          {
            title: gettext('Name'), index: true, name: 'full_name',
            actions: function(id, attributes){
                let participant_name = _this.getParticipantName(attributes)
                return '<a href="/admin/participants/' + attributes['id'] +
                       '" target="_self">' + participant_name + '</a>';
            }
          },
          { title: gettext('Company'), index: true, name: 'organizations_custom_name' },
          { title: gettext('Email'), index: true, name: 'email' },
          {
            title: gettext('Date Added'), index: true, name: 'created_custom_date',
            actions: function(id, attributes) {
              if (attributes['created_custom_date'] != '-' && attributes['created_custom_date'] != '' && typeof attributes['created_custom_date'] != 'undefined')
              {
                 var last_login = attributes['created_custom_date'].split(',')[0].split('/');
                    return '' + last_login[1] + '/' + last_login[2] + '/' + last_login[0];
                }
                return attributes['created_custom_date'];
            }
          },
          { title: gettext('Enrolled In'), index: true, name: 'courses_enrolled',
            actions: function(id, attributes)
            {
              return parseInt(attributes['courses_enrolled']);
            }
          },
          { title: gettext('Activated'), index: true, name: 'active_custom_text' }
        ];
        if (enable_data_deletion == "True"){
          table_columns.push({
            title: " ", name: 'action_buttons',
            actions: function(id, attributes){
              return _this.userDeletionModalManager(_this, id, attributes)
            }
          });
        };
        participantsListViewGrid = new bbGrid.View({
            container: this.$el,
            collection: this.collection.fullCollection,
            colModel: table_columns
          }
        );
        participantsListViewGrid['partial_collection']=this.collection;
        this.$el.find('.bbGrid-container').scroll(this.fetchPages);
        cloneHeader('#participantsListViewGridBlock');
        $(document).on('closed.fndtn.reveal', '#import_from_csv[data-reveal]', function () {
          $('.upload_stats').empty();
          $('#enroll-error-list').empty();
          $('#import_from_csv input[type=checkbox]').attr('disabled', 'disabled');
          $('#import_from_csv input[type=checkbox]').attr('checked', false);
        });
        $(document).on('open.fndtn.reveal', '#import_from_csv[data-reveal]', function () {
          $('#import_from_csv input[type=checkbox]').attr('disabled', 'disabled');
          $('#import_from_csv input[type=checkbox]').attr('checked', false);
        });
        $('#participantsSearchWrapper').on('keyup', 'input', function(){_this.runSearch(_this)});
        $('#companiesAdvancedDeleteButton').on('click','.advancedDeleteOpenModal',function()
        {
          var advanced_delete_modal = '#advanced_delete_modal';
          var errorContainer = $(advanced_delete_modal).find('.errorMessage');
          $(errorContainer).empty();
          $(advanced_delete_modal).find('.closeModal').off().on('click', function()
          {
            $(advanced_delete_modal).find('a.close-reveal-modal').trigger('click');
          });
          $(advanced_delete_modal).foundation('reveal', 'open');
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
              gettext('Admin Company')+
            '</div>'+
            '<div class="participantAdminCompanyValue">'+
              '<input type="text" data-id/>'+
              '<i class="fa fa-check-circle-o correctInput" aria-hidden="true"></i>'+
            '</div>'+
          '</div>'+
          '<div class="large-6 columns participantPermissions">'+
            '<div class="participantPermissionsLabel labelUniversal">'+
              gettext('Admin Permissions')+
            '</div>'+
            '<div class="participantPermissionsValue permissionSelect large-10">'+
              '<input type="text" value='+gettext("Company Admin")+' disabled data-id="company_admin"/>'+
            '</div>'+
            '<i class="fa fa-times removeItem large-2" aria-hidden="true"></i>'+
          '</div>'+
        '</div>';
        var enrollInCourseTemplate = '<div class="row enrollInCourse">'+
          '<div class="large-6 columns participantCourse">'+
            '<div class="participantCourseLabel labelUniversal">'+
              gettext('Course')+
            '</div>'+
            '<div class="participantCourseValue">'+
              '<input type="text" data-id/>'+
              '<i class="fa fa-check-circle-o correctInput" aria-hidden="true"></i>'+
            '</div>'+
          '</div>'+
          '<div class="large-6 columns participantCoursePermissions">'+
            '<div class="participantCoursePermissionsLabel labelUniversal">'+
              gettext('Status')+
            '</div>'+
            '<div class="participantCoursePermissionsValue permissionSelect large-10">'+
              '<select disabled>'+
                '<option value="active">'+gettext('Participant')+'</option>'+
                '<option value="assistant">'+gettext('TA')+'</option>'+
                '<option value="observer">'+gettext('Observer')+'</option>'+
              '</select>'+
            '</div>'+
            '<i class="fa fa-times removeItem large-2" aria-hidden="true"></i>'+
          '</div>'+
        '</div>';
        $('#country_edit').countrySelect({
            defaultCountry: "null",  // set country empty by default on form initialization
            preferredCountries: ["null"]  // put empty country on top of list in drop down
        });

        GetAutocompleteSource(ApiUrls.participant_organization_get_api(), this, 'organization_source');
        GetAutocompleteSource(ApiUrls.participant_courses_get_api(), this, 'course_source');
        var _this = this;
        $('#add_a_participant').on('change', 'input', function()
        {
            $('#add_a_participant').find('.addSingleParticipantButton').removeClass('disabled');
        })
        $('#participantsAddWrapper').find('.participantAddButton').on('click',function()
        {
            if (_this.organization_source)
                GenerateAutocompleteInput(_this.organization_source, '#add_a_participant .participantCompanyValue input');
            else
                InitializeAutocompleteInput(ApiUrls.participant_organization_get_api(), '#add_a_participant .participantCompanyValue input');
            var mainContainer = $('#add_a_participant');
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
            mainContainer.find('.addSingleParticipantButton').addClass('disabled');
            mainContainer.find('.newCompanyCreationPopup').hide();
            mainContainer.foundation('reveal', 'open');

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
        $(document).on('autocomplete_found', function(event, input)
        {
            if (input.parent().hasClass('participantCourseValue'))
                input.parents('.row').find('select').attr('disabled', false);
            else if (input.parent().hasClass('participantCompanyValue'))
                _this.manageNewCompanyPopup(input, false);
        });
        $(document).on('autocomplete_not_found', function(event, input)
        {
            if (input.parent().hasClass('participantCourseValue'))
            {
              input.parents('.row').find('select').attr('disabled', true);
            }
            else if (input.parent().hasClass('participantCompanyValue'))
            {
              var internalAdminFlag = $('#participantsListTopContainer').attr('internal-flag');
              if (internalAdminFlag == 'False')
              {
                _this.manageNewCompanyPopup(input, true);
              }
            }
        });
        $('#add_a_participant').on('click', '.removeItem', function()
        {
            $(this).parents('.row').remove();
        });
        $('#add_a_participant').find('.addSingleParticipantButton').on("click", function()
        {
            if (!$(this).hasClass('disabled'))
            {
                var mainContainer = $('#add_a_participant');
                var data = {}
                $.each($("#add_a_participant form").find(':input'), function(i, v){
                    var input = $(v);
                    var value = input.val().trim();
                    if (value)
                        data[input.attr("name")] = value;

                    if (input.attr("name") == 'country' && data[input.attr("name")] == 'null')
                        data[input.attr("name")] = null;

                    else if (input.attr("name") == 'company')
                    {
                        if (input.attr('data-id').length)
                            data[input.attr("name")] = input.attr('data-id');
                        else if (input.val().trim().length > 0)
                        {
                          var internalAdminFlag = $('#participantsListTopContainer').attr('internal-flag');
                          if (internalAdminFlag == 'False')
                          {
                            data[input.attr("name")] = 0;
                            data["new_company_name"] = value;
                          }
                        }
                    }
                });

                $.each($("#add_a_participant form").find('select'), function(i, v){
                    var input = $(v);
                    if (input.val())
                        data[input.attr("name")] = input.val().trim();
                });

                delete data["undefined"];
                data['course_permissions_list'] = _this.getAllCourses();
                data['company_permissions_list'] = _this.getAllCompanies();
                if (data['company_permissions'] == 'none')
                    data['company_permissions'] = null;
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
    },
    getAllCompanies: function()
    {
      var companyContainer = $('#add_a_participant').find('.adminAnotherCompanyAllWrapper');
      var companyArray = [];
      companyContainer.find('.row').each(function()
      {
        var company = $(this);
        var companyObject = {};
        var companyId = company.find('input').attr('data-id');
        if (companyId != '')
        {
          companyArray.push(companyId);
        }
      });
      return companyArray;
    },
    manageNewCompanyPopup: function(input, showPopup)
    {
      var value = $(input).val().trim();
        if (showPopup && (value.length > 0))
        {
        var testValue = value.replace(/ /g,'');
        if (/^[a-z0-9]+$/i.test(testValue))
        {
          if (value.length <= 30)
          {
            $('#add_a_participant').find('.addSingleParticipantButton').removeClass('disabled');
            $('.participantCompanyValue').find('.errorMessage').empty();
            $(input).parent().find('.newCompanyCreationPopup').show();
          }
          else
          {
            $('#add_a_participant').find('.addSingleParticipantButton').addClass('disabled');
            $('.participantCompanyValue').find('.errorMessage').text(gettext('This company name cannot have more than 30 characters!'));
          }
        }
        else
        {
          $('#add_a_participant').find('.addSingleParticipantButton').addClass('disabled');
          $('.participantCompanyValue').find('.errorMessage').text(gettext('This company name cannot contain non-alphanumeric characters!'));
        }
        }
        else
        {
            $(input).parent().find('.newCompanyCreationPopup').hide();
        }
    },
    userDeletionModalManager: function(_this, id, attributes)
    {
      $(document).on('click', '#button-delete-user-' + id, function(ev){
        var mainContainer = $('#delete_user_modal');
        // Find components on delete modal
        let confirmButton = mainContainer.find('.confirmButton')
        let deletionConfirmationCheckboxes = mainContainer.find('.deletionConfirmationCheckbox');
        // Get row of participant to be deleted
        let row = $(this).closest('tr');
        // Set dialog data
        mainContainer.find('.errorContainer').empty();
        mainContainer.find('.errorContainer').hide();
        mainContainer.find('#participantInfoContainer').html(
          '<table>' +
            '<tr>' +
              '<th>Name</td>' +
              '<th>Company</td>' +
              '<th>Email</td>' +
            '</tr>' +
            '<tr>' +
              '<td>' + _this.getParticipantName(attributes) + '</td>' +
              '<td>' + attributes.organizations_custom_name + '</td>' +
              '<td>' + attributes.email + '</td>' +
            '</tr>' +
          '</table>'
        );

        // Uncheck checkboxes and disable delete button
        deletionConfirmationCheckboxes.removeAttr('checked');
        confirmButton.addClass("disabled");

        deletionConfirmationCheckboxes.off().on('click', function() {
          if (deletionConfirmationCheckboxes.not(':checked').length == 0){
            confirmButton.removeClass('disabled');
          } else {
            confirmButton.addClass("disabled");
          }
        });

        confirmButton.off().on('click', function() {
          if (confirmButton.hasClass("disabled")) {
            return;
          }
          var url = ApiUrls.participants_detail(id);
          var options = {
            url: url,
            type: "DELETE",
          };

          options.headers = { 'X-CSRFToken': $.cookie('apros_csrftoken')};

          $.ajax(options).done(function(data) {
            var confirmationScreen = $('#delete_user_success');
            confirmationScreen.foundation('reveal', 'open');
            row.remove();
          }).fail(function(data) {
              mainContainer.find('.errorContainer').show();
              mainContainer.find('.errorContainer').html("Error encountered - " + data.responseJSON.detail);
            }
          );
        });
      })

      return '<a type="button" data-reveal-id="delete_user_modal" ' +
             'class="button small radius deleteButton"' +
             'id="button-delete-user-' + id + '">' +
             '<i class="fa fa-trash fa-lg actionButtonIcon"/></a>';
    },
    getParticipantName: function(attributes)
    {
      var custom_name = attributes['full_name'];
      if (custom_name === "")
        custom_name=attributes['first_name']+" " +attributes['last_name'];
      if (custom_name === " ")
        custom_name=attributes['username'];

      return custom_name;
    },
    runSearch: function(_this, timeout){
      if (timeout === undefined){
          timeout = 1000;
      }
      if (_this.liveSearchTimer) {
        clearTimeout(_this.liveSearchTimer);
      }
      _this.liveSearchTimer = setTimeout(function() {
        var querryDict = {}
        var searchFlag = false
        $('#participantsSearchWrapper').find('input').each(function(index, value){
          val = $(value);
          name = val.context.name;
          value = val.context.value.trim();
          querryDict[name] = value;
          if (value){
            searchFlag = true
          }
        });

        if (!jQuery.isEmptyObject(querryDict))
        {
          _this.collection.updateQuerryParams(querryDict);
        }

        if(_this.collection.length > 0){
          _this.collection.getFirstPage();
          _this.collection.fullCollection.reset();
        }
        if (searchFlag)
        {
          _this.collection.fetch();
        }
      }, 1000)
    }
});
