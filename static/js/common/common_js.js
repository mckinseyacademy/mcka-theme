$(function() {
    // init plugin (with callback)
    $('.clearable').clearSearch({ callback: function() { 
      $(document).trigger('onClearSearchEvent');
    } } );

    // update value
    $('.clearable').val('').change();
    
    // change width
    $('.clearable').width('200px').change();
});

$(function() {
    // init plugin (with callback)
    $('.clearableParticipantsList').clearSearch({ callback: function() { 
      searchParticipantList();
    } } );

    // update value
    $('.clearableParticipantsList').val('').change();
    
    // change width
    $('.clearableParticipantsList').width('200px').change();
});


searchParticipantList = function() {
  if (this.liveSearchTimer) {
    clearTimeout(this.liveSearchTimer);
  }

  this.liveSearchTimer = setTimeout(function() {
    var querryDict = {}
    $('#participantsSearchWrapper').find('.clearableParticipantsList').each(function(index, value){
      val = $(value);
      val.css("background-color", "white");
      name = val.context.name;
      value = val.context.value.trim();
      if (value) {
        querryDict[name] = value;
      }
    });
    this.participantsListViewGrid.remove();
    var collection = new Apros.collections.Participants();
    if (!jQuery.isEmptyObject(querryDict))
      collection.updateQuerryParams(querryDict);
    var participant_list_view = new Apros.views.ParticipantsInfo({collection: collection, el: '#participantsListViewGridBlock'});
    participant_list_view.render();
  }, 1000)
}

highlightSearchBar = function(item) {
  $('#participantsSearchWrapper').find('.clearableParticipantsList').each(function(index, value){
    val = $(value);
    name = val.context.name;
    if (name == item['tag'])
      val.css("background-color", "#B1C2CC");
  });
}

validateParticipantEmail = function() {
  if (this.liveSearchTimer) {
    clearTimeout(this.liveSearchTimer);
  }

  this.liveSearchTimer = setTimeout(function() {
    var userId = $('#participantsDetailsDataWrapper').attr('data-id');
    var emailObject = $('.participantDetailsEditForm .participantEmailInput');
    var options = {
        url: ApiUrls.validate_participant_email,
        data: {'email': emailObject[0].value, 'userId': userId},
        type: "GET",
        dataType: "json"
      };
    options.headers = { 'X-CSRFToken': $.cookie('apros_csrftoken')};
    $.ajax(options)
    .done(function(data) {
      var checkMark = $('.participantDetailsEditForm .checkMark');
      var emailText = $('.participantDetailsEditForm .emailText');
      var saveChangeButton = $('.participantDetailsEditForm .participantDetailsSave'); 
      emailText.hide();
      checkMark.hide();
      if(data['status'] == 'notTakenEmail'){
        checkMark.css('display', 'inline');
        checkMark.show();
        saveChangeButton.removeClass('disabled');
      }
      else if(data['status'] == 'takenEmail'){
        emailText.show();
        saveChangeButton.addClass('disabled');
      }
      else if(data['status'] == 'hisEmail'){
        emailText.hide();
        checkMark.hide();
        saveChangeButton.removeClass('disabled');
      }
    })
    .fail(function(data) {
      console.log("Ajax failed to fetch data");
    });
  }, 1000)
}