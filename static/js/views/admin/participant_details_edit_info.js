 Apros.views.ParticipantEditDetailsView = Backbone.View.extend({
    initialize: function(options){
      var _this=this;
      _this.enroll_user_in_course_function();
      _this.setLocationTooltip(); 
      $('#country_edit').countrySelect();
      InitializeAutocompleteInput(options.url, 'form.participantDetailsEditForm .participantCompanyValue input');
      $('#participantDetailsWrapper').find('.newCompanyCreationPopup').hide();
      $(document).on('autocomplete_found', function(event, input)
      {
        if (input.parent().hasClass('participantCompanyValue'))
        {
          $('#participantDetailsWrapper').find('.errorMessage').empty();
          _this.manageNewCompanyPopup(input, false);
        }
      });
      $(document).on('autocomplete_not_found', function(event, input)
      {
        if (input.parent().hasClass('participantCompanyValue'))
        {
          $('#participantDetailsWrapper').find('.errorMessage').empty();
          _this.manageNewCompanyPopup(input, true);
        }
      });
      $('#participantDetailsWrapper').find('.participantEditDetails').off().on("click", function()
      {
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
            $("#country_edit").countrySelect("selectCountry", 'us');
        }
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
          $.each($("form").find(':input'), function(i, v){
            var input = $(v);
            data[input.attr("name")] = input.val().trim();
            if (input.attr("name") == 'company')
            {
              data['company'] = input.attr('data-id');  
              data['company_old'] = input.attr('data-old-id');
            }
          });
          delete data["undefined"];
          var xcsrf = data['csrfmiddlewaretoken'];
          delete data['csrfmiddlewaretoken'];
          $.ajax({
            type: 'POST',
            url: '/admin/participants/'+id,
            headers: { 'X-CSRFToken': xcsrf },
            data: data,
            dataType: "json",
            cache: false,
            success: function (data, status) {
                if (data['status'] == "ok") {
                  _this.setLocationTooltip(); 
                  _this.update_participant_field_data();
                  var company = $('#participantDetailsWrapper').find('.participantDetailsEditForm').find('.participantCompanyValue input');
                  company.attr('data-old-id',company.attr('data-id'));
                  $('#participantDetailsMainModal').find('.mainText').text('Updated user data!');
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
      var company_data_id = edit.find('.participantCompanyValue input').attr('data-id');
      details.find('.participantCompanyValue a').attr('data-id',company_data_id);
      var company_href = details.find('.participantCompanyValue a').attr('href')
      company_href = company_href.substring(0, company_href.lastIndexOf('/')) + '/';
      details.find('.participantCompanyValue a').attr('href',company_href + company_data_id);
      var genderAbbreviation = edit.find('.participantGenderValue select').val();
      if (genderAbbreviation == 'M')
        details.find('.participantGenderValue').text('Male');
      if (genderAbbreviation == 'F')
        details.find('.participantGenderValue').text('Female');
      var city = edit.find('.participantCityValue input').val().trim();
      var country = edit.find('#country_edit_code').val().trim().toUpperCase();
      combinedLocation = city + ', ' + country;
      if (city === "" && country != "")
        combinedLocation = country;
      else if (country === "" && city != "")
        combinedLocation = city;
      else if (city === "" && country === "")
        combinedLocation = "N/A";
      
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
      if (fullGender == 'Female')
        edit.find('.participantGenderValue select').val('F');
      if (fullGender == 'Male')
        edit.find('.participantGenderValue select').val('M');
      var locationText = details.find('.participantLocationValue').text();
      if (locationText.indexOf(',') > -1)
      {
        edit.find('.participantCityValue input').val(locationText.split(',')[0].trim())
        edit.find('#country_edit_code').val(locationText.split(',')[1].trim().toLowerCase())
        var selected_country = $("#country_edit_code").val();
        if(_this.check_if_country_exist(selected_country))
          $("#country_edit").countrySelect("selectCountry", selected_country);
        else
          $("#country_edit").countrySelect("selectCountry", 'us');
      }
    },
    setLocationTooltip: function()
    {
      var details = $('#participantDetailsWrapper').find('.participantDetailsWrapper');
      var locationText = details.find('.participantLocationValue').text().trim();
      if ((locationText.indexOf(',') > -1) || (locationText.length == 2))
      {
        var tooltipText = '';
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
        $('#participantDetailsWrapper').find('.participantDetailsWrapper .participantLocationValue').attr('title', tooltipText);
      }
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
        $(enroll_modal_id).find('.participantModalTitle').text('Select Course');
        $(enroll_modal_id).find('.participantModalDescription').text('User will be enrolled in course selected below.');
        $(enroll_modal_id).find('.participantModalContent').html(
          '<div class="row enrollParticipants">' +
          '<div class="large-6 columns enrollParticipantsCourse">' +
          '<p class="labelUnirvesal">Course</p>' +
          '<input type="text" value="" name="course" maxlength="60">' +
          '</div>' +
          '<div class="large-6 columns enrollParticipantsStatus">' +
          '<p class="labelUnirvesal">Status</p>' +
          '<select name="status">' +
          '<option value="Active">Active</option>' +
          '<option value="Observer">Observer</option>' +
          '<option value="TA">TA</option></select>' +
          '</div></div>'
        );
        var url = ApiUrls.participant_courses_get_api();
        InitializeAutocompleteInput(url, '.enrollParticipantsCourse input');
        $(enroll_modal_id).find('.participantModalControl').find('.cancelChanges').off().on('click', function()
        {
          $(enroll_modal_id).find('a.close-reveal-modal').trigger('click');
        });
        var saveButton = $(enroll_modal_id).find('.participantModalControl').find('.saveChanges');
        saveButton.text('Enroll Participant');
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
                alert('You need to select status!');
                return;
              }
          }
          else
          {
            alert('You need to select status!');
            return;
          }
          var course_id = $('.enrollParticipantsCourse input').attr('data-id');
          if (!course_id){
            alert('You need to select course!');
            return;
          }
          if (course_id.length == 0) {
            alert('You need to select course!');
            return;
          }
          var dictionaryToSend = {"status": selectedVal};
          var url = ApiUrls.participant_manage_courses(user_id,course_id);
          var options = {
            url: url,
            data: dictionaryToSend,
            type: "POST",
            dataType: "json"
          };

          options.headers = { 'X-CSRFToken': $.cookie('apros_csrftoken')};
          saveButton.attr('disabled', 'disabled');
          saveButton.addClass('disabled');
          $.ajax(options)
          .done(function(data) {
            if (data["status"] == "success")
            {
              alert("User successfully enrolled in course");
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
        var testValue = value.replace(' ','');
        if (/^[a-z0-9]+$/i.test(testValue)) 
        {
          $('#participantDetailsWrapper').find('.participantDetailsEditForm').find('.participantDetailsSave').removeClass('disabled');
          $('#participantDetailsWrapper').find('.errorMessage').empty();
          $(input).parent().find('.newCompanyCreationPopup').show();
        }
        else
        {
          $('#participantDetailsWrapper').find('.participantDetailsEditForm').find('.participantDetailsSave').addClass('disabled');
          $('.participantCompanyValue').find('.errorMessage').text('This company name cannot contain non-alphanumeric characters!');
        }
      }
      else
      {
        $(input).parent().find('.newCompanyCreationPopup').hide();
      }
    }
  });