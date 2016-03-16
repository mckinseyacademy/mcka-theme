 Apros.views.ParticipantEditDetailsView = Backbone.View.extend({
    initialize: function(){
      var _this=this;
      $('#participantDetailsWrapper').find('.participantEditDetails').off();
      $('#participantDetailsWrapper').find('.participantEditDetails').on("click", function()
      {
        $('#participantDetailsWrapper').find('.participantDetailsWrapper').hide();
        $('#participantDetailsWrapper').find('.participantDetailsEditForm').find('.participantDetailsSave').addClass('disabled');
        $('#participantDetailsWrapper').find('.participantDetailsEditForm').show();

      });
      $('#participantDetailsWrapper').find('.cancelParticipantEdit').off();
      $('#participantDetailsWrapper').find('.cancelParticipantEdit').on("click", function()
      {
        $('#participantDetailsWrapper').find('.participantDetailsEditForm').hide();
        $('#participantDetailsWrapper').find('.participantDetailsEditForm').find('.participantDetailsSave').addClass('disabled');
        $('#participantDetailsWrapper').find('.participantDetailsWrapper').show();
        
        _this.update_edit_field_data();
      });
      $('#participantDetailsWrapper').find('.participantDetailsEditForm').find('input').off('focus');
      $('#participantDetailsWrapper').find('.participantDetailsEditForm').find('input').on("focus", function()
      {
        $('#participantDetailsWrapper').find('.participantDetailsEditForm').find('.participantDetailsSave').removeClass('disabled');
      });
      $('#participantDetailsWrapper').find('.participantDetailsEditForm').find('.participantDetailsSave').on("click", function()
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
      details.find('.participantGenderValue').text(edit.find('.participantGenderValue select').val());
      var city = edit.find('.participantCityValue input').val().trim();
      var country = edit.find('.participantCountryValue input').val().trim();
      combinedLocation = edit.find('.participantCityValue input').val().trim() + ', ' + edit.find('.participantCountryValue input').val().trim();
      if (city === "" && country != "")
        combinedLocation = edit.find('.participantCountryValue input').val().trim();
      else if (country === "" && city != "")
        combinedLocation = edit.find('.participantCityValue input').val().trim();
      else if (city === "" && country === "")
        combinedLocation = "N/A";
      
      details.find('.participantLocationValue').text(combinedLocation);
      $('#participantsTopDetailsContainer').find('.participantFullName').text(edit.find('.participantFirstNameValue input').val() + ' ' + edit.find('.participantLastNameValue input').val());
    },

    update_edit_field_data: function()
    {
      var details = $('#participantDetailsWrapper').find('.participantDetailsWrapper');
      var edit = $('#participantDetailsWrapper').find('.participantDetailsEditForm');
      edit.find('.participantFirstNameValue input').val(details.find('.participantFirstNameValue').text().trim());
      edit.find('.participantLastNameValue input').val(details.find('.participantLastNameValue').text().trim());
      edit.find('.participantUsernameValue input').val(details.find('.participantUsernameValue').text().trim());
      edit.find('.participantEmailValue input').val(details.find('.participantEmailValue').text().trim());
      edit.find('.participantCompanyValue input').val(details.find('.participantCompanyValue').text().trim());
      edit.find('.participantGenderValue select').val(details.find('.participantGenderValue').text().trim());
      var locationText = details.find('.participantLocationValue').text();
      if (locationText.indexOf(',') > -1)
      {
        edit.find('.participantCityValue input').val(locationText.split(',')[0].trim())
        edit.find('.participantCountryValue input').val(locationText.split(',')[1].trim())
      }
    }
  });