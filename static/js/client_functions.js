function AdjustCompanyParticiantsNumber(client_id, parentContainer, urlParams)
{
  var options = {
    url: ApiUrls.cached_resource_api("organizations/"+client_id+"/courses"),
    type: "GET",
    dataType: "json",
    data:urlParams,
    timeout: 1000000,
    beforeSend: function( xhr ) {
      xhr.setRequestHeader("X-CSRFToken", $.cookie('apros_csrftoken'));
    }
  };
  $.ajax(options)
  .done(function(data) {
    var participant_number_container;
    for (var i=0;i<data.length;i++)
    {
      participant_number_container = $(parentContainer).find("#"+data[i]["id"].replace( /(:|\.|\[|\]|\\|\/|,)/g, "\\$1" )).parent().find(".companyParticipantsNumber");
      participant_number_container.empty();
      participant_number_container.text(data[i]["enrolled_users"].length);
    }
    $(".loadingCompanyParticipantNumber").each(function(){
      $(this).parent().empty().text("0");
    });

  })
  .fail(function(data) {
    console.log("Ajax failed to fetch data");
    console.log(data)
  });
};