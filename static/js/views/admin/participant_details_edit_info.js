 Apros.views.ParticipantEditDetailsView = Backbone.View.extend({
    initialize: function(){
      var _this=this;
      $('#country_edit').countrySelect();     
      _this.initialize_user_organizations();
      $('#participantDetailsWrapper').find('.participantEditDetails').off().on("click", function()
      {
        $('#participantDetailsWrapper').find('.participantDetailsWrapper').hide();
        $('#participantDetailsWrapper').find('.participantDetailsEditForm').find('.participantDetailsSave').addClass('disabled');
        $('#participantDetailsWrapper').find('.participantDetailsEditForm').show();
        var details = $('#participantDetailsWrapper').find('.participantDetailsWrapper');
        var locationText = details.find('.participantLocationValue').text();
        if (locationText.indexOf(',') > -1)
        {
          var country = locationText.split(',')[1].trim().toLowerCase();
          if (_this.check_if_country_exist(country))
            $("#country_edit").countrySelect("selectCountry", country);
        }
      });
      $('#participantDetailsWrapper').find('.cancelParticipantEdit').off().on("click", function()
      {
        $('#participantDetailsWrapper').find('.participantDetailsEditForm').hide();
        $('#participantDetailsWrapper').find('.participantDetailsEditForm').find('.participantDetailsSave').addClass('disabled');
        $('#participantDetailsWrapper').find('.participantDetailsWrapper').show();
        
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
                  _this.update_participant_field_data();
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
      details.find('.participantCompanyValue').text(edit.find('.participantCompanyValue input').val());
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
      edit.find('.participantCompanyValue input').val(details.find('.participantCompanyValue').text().trim());
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
      }
    },
    initialize_user_organizations: function()
    {
      var projects = [
        {
          value: "jquery",
          label: "jQuery",
          desc: "the write less, do more, JavaScript library",
          icon: "jquery_32x32.png"
        },
        {
          value: "jquery-ui",
          label: "jQuery UI",
          desc: "the official user interface library for jQuery",
          icon: "jqueryui_32x32.png"
        },
        {
          value: "sizzlejs",
          label: "Sizzle JS",
          desc: "a pure-JavaScript CSS selector engine",
          icon: "sizzlejs_32x32.png"
        }
      ];
   
    $( "#project" ).autocomplete({
      minLength: 2,
      source: function()
      {
        
      },
      focus: function( event, ui ) {
        $( "#project" ).val( ui.item.label );
        return false;
      },
      select: function( event, ui ) {
          $( "#project" ).val( ui.item.label );
          $( "#project-id" ).val( ui.item.value );
          $( "#project-description" ).html( ui.item.desc );
          $( "#project-icon" ).attr( "src", "images/" + ui.item.icon );
   
          return false;
        }
      });
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
    } 
  });