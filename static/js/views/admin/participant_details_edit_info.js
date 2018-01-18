 Apros.views.ParticipantEditDetailsView = Backbone.View.extend({
    initialize: function(options){
      $('#mainParticipantsDetailsWrapper').on('click', '.participantDetailsNavigationButtonCompanyAdmin', function(event){
        event.preventDefault();
        window.history.back();
      });

      var _this=this;
      var _options=options;
      _this.enroll_user_in_course_function();
      _this.setLocationTooltip();
      $('#country_edit').countrySelect({
        defaultCountry: "null",  // set country empty by default on form initialization
        preferredCountries: ["null"]  // put empty country on top of list in drop down

      });
      InitializeAutocompleteInput(options.url, 'form.participantDetailsEditForm .participantCompanyValue input');
      $('#participantDetailsWrapper').find('.newCompanyCreationPopup').hide();
      $(document).on('autocomplete_found', function(event, input)
      {
        if (input.parent().hasClass('participantCompanyValue') || (input.parent().hasClass('participantAdminCompanyValue')))
        {
          $('#participantDetailsWrapper').find('.errorMessage').empty();
          _this.manageNewCompanyPopup(input, false);
        }
      });
      $(document).on('autocomplete_not_found', function(event, input)
      {
        if (input.parent().hasClass('participantCompanyValue') || (input.parent().hasClass('participantAdminCompanyValue')))
        {
          $('#participantDetailsWrapper').find('.errorMessage').empty();
          var internalAdminFlag = $('#participantsDetailsDataWrapper').attr('internal-flag');
          if (internalAdminFlag == 'False')
          {
            _this.manageNewCompanyPopup(input, true);
          }
        }
      });
      $('#participantDetailsWrapper').find('.participantEditDetails').off().on("click", function()
      {
        _this.generateCompanyAdminRights(_this.user_id, _this.adminAnotherCompanyTemplate, $('#participantDetailsWrapper').find('.companyAdminRolesContainer'));
        var cont = $('#participantDetailsWrapper');
        cont.find('.participantDetailsWrapper').hide();
        cont.find('.participantDetailsEditForm').find('.participantDetailsSave').addClass('disabled');
        cont.find('.participantDetailsEditForm').show();
        var details = $('#participantDetailsWrapper').find('.participantDetailsWrapper');
        var locationText = details.find('.participantLocationValue').text();
        if (locationText.indexOf(',') > -1)
        {
          var country = locationText.split(',')[1].trim().toLowerCase();
          if (_this.check_if_country_exist(country))
            $("#country_edit").countrySelect("selectCountry", country);
          else
            $("#country_edit").countrySelect("selectCountry", 'null');
        }
      });
      $('#participantDetailsWrapper').find('.companyAdminRolesContainer').on("focus", "input", function(){
        $('#participantDetailsWrapper').find('.participantDetailsEditForm').find('.participantDetailsSave').removeClass('disabled');
      });
      $('#participantDetailsWrapper').find('.cancelParticipantEdit').off().on("click", function()
      {
        var cont = $('#participantDetailsWrapper');
        cont.find('.participantDetailsEditForm').hide();
        cont.find('.participantDetailsEditForm').find('.participantDetailsSave').addClass('disabled');
        cont.find('.participantDetailsWrapper').show();
        _this.setLocationTooltip(); 
        _this.update_edit_field_data(_this);
      });
      $('#participantDetailsWrapper .participantDetailsEditForm').on('click', '.addAnotherCompanyToAdminister a', function(event)
      {
        event.preventDefault();
        var objectContainer = $('#participantDetailsWrapper').find('.companyAdminRolesContainer');
        objectContainer.append(_this.adminAnotherCompanyTemplate);
        var appendedChild = objectContainer.children().last().find('.participantAdminCompanyValue input');
        if (_this.organization_source)
          GenerateAutocompleteInput(_this.organization_source, appendedChild);
        else
          InitializeAutocompleteInput(ApiUrls.participant_organization_get_api(), appendedChild);
      });
      $('#participantDetailsWrapper .participantDetailsEditForm').on('click', '.removeItem', function()
      {
        $(this).parents('.row').remove();
        $('#participantDetailsWrapper').find('.participantDetailsEditForm').find('.participantDetailsSave').removeClass('disabled');
      });
      $('#participantDetailsWrapper .participantDetailsEditForm').on('click', '.refreshCompanyToAdminister', function()
      {
        _this.generateCompanyAdminRights(_this.user_id, _this.adminAnotherCompanyTemplate, $('#participantDetailsWrapper').find('.companyAdminRolesContainer'));
      });
      $('#participantDetailsWrapper').find('.participantDetailsEditForm').find('input').off('focus').on("focus", function()
      { 
        var canSave = true
        $.each($("form").find(':input'), function(i, v){
            if ($(v).hasClass('validationError')){
              canSave = false
            }  
          });
        if (canSave)
          $('#participantDetailsWrapper').find('.participantDetailsEditForm').find('.participantDetailsSave').removeClass('disabled');
      });
      $('#participantDetailsWrapper').find('.participantDetailsEditForm').find('.participantDetailsSave').off().on("click", function()
      {
        if (!$(this).hasClass('disabled'))
        {
          var id = $('#participantsDetailsDataWrapper').attr('data-id');
          var data = {}
          var validation_fail = false;
          var validation_message = "";    
          $.each($("form").find(':input'), function(i, v){
            var input = $(v);
            data[input.attr("name")] = input.val().trim();
            if (input.attr("name") == "username" && data[input.attr("name")].length == 0)
            {
              validation_message += gettext("Username can't be empty! ");
              validation_fail = true;
            }
            else if (input.attr("name") == "first_name" && data[input.attr("name")].length == 0)
            {
              validation_message += gettext("First name can't be empty! ");
              validation_fail = true;
            }
            else if (input.attr("name") == "last_name" && data[input.attr("name")].length == 0)
            {
              validation_message += gettext("Last name can't be empty! ");
              validation_fail = true;
            }
            else if (input.attr("name") == "email" && data[input.attr("name")].length == 0)
            {
              validation_message += gettext("Email can't be empty! ");
              validation_fail = true;
            }

            if (input.attr("name") == 'country' && data[input.attr("name")] == 'null')
            {
              data[input.attr("name")] = '';
            }
            if (input.attr("name") == 'company')
            {
              if (input.attr('data-id').length)
              {
                data[input.attr("name")] = input.attr('data-id');
              }
              else if (input.val().trim().length > 0)
              {
                var internalAdminFlag = $('#participantsDetailsDataWrapper').attr('internal-flag');
                if (internalAdminFlag == 'False')
                {
                  data[input.attr("name")] = 0;
                  data["new_company_name"] = input.val().trim();
                }
                else
                {
                  validation_message += gettext("Company doesn't exist! ");
                  validation_fail = true;
                }
              }
              if (input.attr('data-old-id'))
              {
                data['company_old'] = input.attr('data-old-id');
              }
              else
              {
                data['company_old'] = 0;
              }
            }
            if (input.attr("name") == 'company_permissions')
              if (input.attr('data-old-permission'))
              {
                data['company_permissions_old'] = input.attr('data-old-permission');
              }
              else
              {
                data['company_permissions_old'] = "none";
              }
          });
          if (validation_fail)
          {
            alert(validation_message);
            return;
          }
          delete data["undefined"];
          var xcsrf = data['csrfmiddlewaretoken'];
          delete data['csrfmiddlewaretoken'];
          _this.updateCompanyAdminPermissions();
          $.ajax({
            type: 'POST',
            url: '/admin/participants/'+id,
            beforeSend: function( xhr ) {
              xhr.setRequestHeader("X-CSRFToken", xcsrf);
            },
            data: data,
            dataType: "json",
            cache: false,
            success: function (data, status) {
                if (data['status'] == "ok") {
                  _this.setLocationTooltip();
                  _this.update_participant_field_data();
                  InitializeAutocompleteInput(_options.url, 'form.participantDetailsEditForm .participantCompanyValue input');
                  var company = $('#participantDetailsWrapper').find('.participantDetailsEditForm').find('.participantCompanyValue input');
                  company.attr('data-old-id',data['company']);
                  var company_permissions = $('#participantDetailsWrapper').find('.participantDetailsEditForm').find('.participantPermissionsValue select');
                  company_permissions.attr('data-old-permission',data['company_permissions']);
                  $('#participantDetailsMainModal').find('.mainText').text(gettext('Updated user data!'));
                  $('#participantDetailsMainModal').foundation('reveal', 'open');
                  $('#participantDetailsWrapper').find('.cancelParticipantEdit').click();
                }
                else {
                  if (data['type'] == 'validation_failed')
                  {
                    var message = '';
                    for (key in data['message'])
                    {
                      message += key + ' - ' + data['message'][key] + '\n';
                    }
                    $('#participantDetailsMainModal').find('.mainText').text(message);
                    $('#participantDetailsMainModal').foundation('reveal', 'open');
                  }
                  else
                  {
                    $('#participantDetailsMainModal').find('.mainText').text(data['message']);
                    $('#participantDetailsMainModal').foundation('reveal', 'open');
                  }
                }
              },
              error: function(data, status)
              {
                $('#participantDetailsMainModal').find('.mainText').text(data['responseText']);
                $('#participantDetailsMainModal').foundation('reveal', 'open');
              }
          });
        }
      });
    },
    render: function(){
      
    },
    update_participant_field_data: function()
    {
      var details = $('#participantDetailsWrapper').find('.participantDetailsWrapper');
      var edit = $('#participantDetailsWrapper').find('.participantDetailsEditForm');
      details.find('.participantFirstNameValue').text(edit.find('.participantFirstNameValue input').val());
      details.find('.participantLastNameValue').text(edit.find('.participantLastNameValue input').val());
      details.find('.participantUsernameValue').text(edit.find('.participantUsernameValue input').val());
      details.find('.participantEmailValue').text(edit.find('.participantEmailValue input').val());
      details.find('.participantCompanyValue a').text(edit.find('.participantCompanyValue input').val());
      details.find('.participantPermissionsValue').text(edit.find('.participantPermissionsValue select option:selected').text());
      var company_data_id = edit.find('.participantCompanyValue input').attr('data-id');
      details.find('.participantCompanyValue a').attr('data-id',company_data_id);
      var company_href = details.find('.participantCompanyValue a').attr('href')
      company_href = company_href.substring(0, company_href.lastIndexOf('/')) + '/';
      details.find('.participantCompanyValue a').attr('href',company_href + company_data_id);
      var genderAbbreviation = edit.find('.participantGenderValue select').val();
      if (genderAbbreviation == 'M')
        details.find('.participantGenderValue').text(gettext('Male'));
      else if (genderAbbreviation == 'F')
        details.find('.participantGenderValue').text(gettext('Female'));
      else
        details.find('.participantGenderValue').text('');

      var city = edit.find('.participantCityValue input').val().trim();
      var country = edit.find('#country_edit_code').val().trim().toUpperCase();
      combinedLocation = city + ', ' + country;
      if (city === "" && (country != "" && country != 'NULL'))
        combinedLocation = country;
      else if ((country === "" || country === "NULL") && city != "")
        combinedLocation = city;
      else if (city === "" && (country === "" || country === "NULL"))
        combinedLocation = "—";
      
      details.find('.participantLocationValue').text(combinedLocation);
      $('#participantsTopDetailsContainer').find('.participantFullName').text(edit.find('.participantFirstNameValue input').val() + ' ' + edit.find('.participantLastNameValue input').val());
    },

    update_edit_field_data: function(_this)
    {
      var details = $('#participantDetailsWrapper').find('.participantDetailsWrapper');
      var edit = $('#participantDetailsWrapper').find('.participantDetailsEditForm');
      edit.find('.participantFirstNameValue input').val(details.find('.participantFirstNameValue').text().trim());
      edit.find('.participantLastNameValue input').val(details.find('.participantLastNameValue').text().trim());
      edit.find('.participantUsernameValue input').val(details.find('.participantUsernameValue').text().trim());
      edit.find('.participantEmailValue input').val(details.find('.participantEmailValue').text().trim());
      edit.find('.participantCompanyValue input').val(details.find('.participantCompanyValue a').text().trim());
      edit.find('.participantCompanyValue input').attr('data-id',details.find('.participantCompanyValue a').attr('data-id'));
      var fullGender = details.find('.participantGenderValue').text().trim();
      if (fullGender == gettext('Female'))
        edit.find('.participantGenderValue select').val('F');
      else if (fullGender == gettext('Male'))
        edit.find('.participantGenderValue select').val('M');
      else
        edit.find('.participantGenderValue select').val('');

      var locationText = details.find('.participantLocationValue').text();
      if (locationText.indexOf(',') > -1)
      {
        edit.find('.participantCityValue input').val(locationText.split(',')[0].trim())
        edit.find('#country_edit_code').val(locationText.split(',')[1].trim().toLowerCase())
        var selected_country = $("#country_edit_code").val();
        if(_this.check_if_country_exist(selected_country))
          $("#country_edit").countrySelect("selectCountry", selected_country);
        else
          $("#country_edit").countrySelect("selectCountry", 'null');
      }
    },
    setLocationTooltip: function()
    {
      var details = $('#participantDetailsWrapper').find('.participantDetailsWrapper');
      var locationText = details.find('.participantLocationValue').text().trim();
      var tooltipText = locationText;

      if ((locationText.indexOf(',') > -1) || (locationText.length == 2))
      {
        tooltipText = '';
        var name = '';
        if (locationText.length == 2)
        {
          name = locationText.toLowerCase();
        }
        else
        {
          tooltipText = locationText.split(',')[0].trim();
          name = locationText.split(',')[1].trim().toLowerCase();
        }

        var selectableCountries = $.fn['countrySelect'].getCountryData();
        for (var i = 0; i<selectableCountries.length;i++)
        { 
          if (selectableCountries[i].iso2 == name)
          {
            tooltipText += ', ' + selectableCountries[i].name;
            break;
          }  
        }
      }
      $('#participantDetailsWrapper').find('.participantDetailsWrapper .participantLocationValue').attr('title', tooltipText);

    },
    check_if_country_exist: function(name)
    {
      var selectableCountries = $.fn['countrySelect'].getCountryData();
      for (var i = 0; i<selectableCountries.length;i++)
      {
        if (selectableCountries[i].iso2 == name)
          return true;
      }
      return false;
    },
    enroll_user_in_course_function: function()
    {
      $('#participantsDetailsDataWrapper').on('click','.participantEnrollInCourse',function()
      {
        if ($(this).hasClass('disabled'))
          return;
        var user_id = $("#participantsDetailsDataWrapper").attr('data-id');
        var enroll_modal_id = '#participantEnrollMainModal';
        $(enroll_modal_id).find('.participantModalTitle').text(gettext('Select Course'));
        $(enroll_modal_id).find('.participantModalDescription').text(gettext('User will be enrolled in course selected below.'));
        $(enroll_modal_id).find('.participantModalContent').html(
          '<div class="row enrollParticipants">' +
          '<div class="large-6 columns enrollParticipantsCourse">' +
          '<p class="labelUnirvesal"> '+ gettext('Course') + ' </p>' +
          '<input type="text" value="" name="course" maxlength="60">' +
          '</div>' +
          '<div class="large-6 columns enrollParticipantsStatus">' +
          '<p class="labelUnirvesal">' + gettext('Status') +'</p>' +
          '<select name="status">' +
          '<option value="Active">'+gettext('Participant')+'</option>' +
          '<option value="Observer">' + gettext('Observer') + '</option>' +
          '<option value="TA">' + gettext('TA') + '</option></select>' +
          '</div></div>'
        );
        var url = ApiUrls.participant_courses_get_api();
        InitializeAutocompleteInput(url, '.enrollParticipantsCourse input');
        $(enroll_modal_id).find('.participantModalControl').find('.cancelChanges').off().on('click', function()
        {
          $(enroll_modal_id).find('a.close-reveal-modal').trigger('click');
        });
        var saveButton = $(enroll_modal_id).find('.participantModalControl').find('.saveChanges');
        saveButton.text(gettext('Enroll Participant'));
        saveButton.attr('disabled', 'disabled');
        saveButton.addClass('disabled');
        $(document).on('autocomplete_found', function(event, input){
          var course_id = $('.enrollParticipantsCourse input').attr('data-id');
          if (course_id){
            input.parents(enroll_modal_id).find('.participantModalControl .saveChanges').removeAttr('disabled');
            input.parents(enroll_modal_id).find('.participantModalControl .saveChanges').removeClass('disabled');
          }
        });
        $(document).on('autocomplete_not_found', function(event, input){
          input.parents(enroll_modal_id).find('.participantModalControl .saveChanges').attr('disabled', 'disabled');
          input.parents(enroll_modal_id).find('.participantModalControl .saveChanges').addClass('disabled');
        });
        saveButton.off().on('click', function()
        {
          if ($(this).hasClass('disabled'))
            return;
          var selectedVal = "";
          var selected = $('.enrollParticipantsStatus select');
          if (selected.length > 0) {
              selectedVal = selected.val();
              if(!selectedVal){
                alert(gettext('You need to select status!'));
                return;
              }
          }
          else
          {
            alert(gettext('You need to select status!'));
            return;
          }
          var course_id = $('.enrollParticipantsCourse input').attr('data-id');
          if (!course_id){
            alert(gettext('You need to select course!'));
            return;
          }
          if (course_id.length == 0) {
            alert(gettext('You need to select course!'));
            return;
          }
          var dictionaryToSend = {"status": selectedVal};
          var url = ApiUrls.participant_manage_courses(user_id,course_id);
          var options = {
            url: url,
            data: dictionaryToSend,
            type: "POST",
            dataType: "json",
            beforeSend: function( xhr ) {
              xhr.setRequestHeader("X-CSRFToken", $.cookie('apros_csrftoken'));
            },
          };
          saveButton.attr('disabled', 'disabled');
          saveButton.addClass('disabled');
          $.ajax(options)
          .done(function(data) {
            if (data["status"] == "success")
            {
              alert(gettext("User successfully enrolled in course"));
              $(enroll_modal_id).find('a.close-reveal-modal').trigger('click');
            }
            else if (data["status"] == "error")
            {
              alert(data["message"]);
            }
            })
          .fail(function(data) {
            console.log("Ajax failed to fetch data");
            console.log(data);
            })
          });
          $(enroll_modal_id).foundation('reveal', 'open');
      }); 
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
            $('#participantDetailsWrapper').find('.participantDetailsEditForm').find('.participantDetailsSave').removeClass('disabled');
            $('#participantDetailsWrapper').find('.errorMessage').empty();
            $(input).parent().find('.newCompanyCreationPopup').show();
          }
          else
          {
            $('#participantDetailsWrapper').find('.participantDetailsEditForm').find('.participantDetailsSave').addClass('disabled');
            $('.participantCompanyValue').find('.errorMessage').text(gettext('This company name cannot have more than 30 characters!'));
          }
        }
        else
        {
          $('#participantDetailsWrapper').find('.participantDetailsEditForm').find('.participantDetailsSave').addClass('disabled');
          $('.participantCompanyValue').find('.errorMessage').text(gettext('This company name cannot contain non-alphanumeric characters!'));
        }
      }
      else
      {
        $(input).parent().find('.newCompanyCreationPopup').hide();
      }
    },
    updateCompanyAdminPermissions: function()
    {
      var list_of_company_ids = [];
      var container = $('#participantDetailsWrapper').find('.companyAdminRolesContainer')
      container.find('.participantAdminCompanyValue input').each(function()
      {
        var id = $(this).attr("data-id");
        if (id != "")
          list_of_company_ids.push(parseInt(id));
      });
      PutUserAdminCompanies(this.user_id, list_of_company_ids);
    },
    generateCompanyAdminRights: function(user_id, template, container)
    {
      GetUserAdminCompanies(user_id);
      $(container).empty();
      $(container).append('<i class="fa fa-spinner fa-spin"></i>')
      $(document).on("admin_companies_get", function(event, data)
      {
        var objectContainer = $(container);
        objectContainer.empty();
        var companies = data.company_list;
        for (var i = 0; i<companies.length; i++)
        {
          objectContainer.append(template);
          var appendedChild = objectContainer.children().last().find('.participantAdminCompanyValue input');
          appendedChild.attr("data-id", companies[i].id);
          appendedChild.val(companies[i].display_name);
          if (this.organization_source)
              GenerateAutocompleteInput(this.organization_source, appendedChild);
          else
              InitializeAutocompleteInput(ApiUrls.participant_organization_get_api(), appendedChild);
        }
      });
    },
    user_id: $("#participantsDetailsDataWrapper").attr('data-id'),
    adminAnotherCompanyTemplate: '<div class="row adminAnotherCompany">'+
          '<div class="large-6 columns participantAdminCompany">'+
            '<div class="participantAdminCompanyLabel labelUniversal">'+
              gettext('Admin Company') +
            '</div>'+
            '<div class="participantAdminCompanyValue">'+
              '<input type="text" data-id/>'+
              '<div class="newCompanyCreationPopup">' + gettext('Try selecting your company from the type-ahead results.') + '</div>'+
              '<i class="fa fa-check-circle-o correctInput" aria-hidden="true"></i>'+
            '</div>'+
          '</div>'+
          '<div class="large-6 columns participantPermissions">'+
            '<div class="participantPermissionsLabel labelUniversal">'+
              gettext('Admin Permissions') +
            '</div>'+
            '<div class="participantPermissionsValue permissionSelect large-10">'+
              '<input type="text" value='+gettext("Company Admin")+' disabled data-id="company_admin"/>'+
            '</div>'+
            '<i class="fa fa-times removeItem large-2" aria-hidden="true"></i>'+
          '</div>'+
        '</div>'
  });
