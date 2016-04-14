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
    var validationObject = $('.participantDetailsEditForm .participantEmailInput');
    var checkMark = $('.participantEmail .checkMark');
    var warningText = $('.participantEmail .warningText');
    var options = {
        url: ApiUrls.validate_participant_email,
        data: {'email': validationObject[0].value, 'userId': userId},
        type: "GET",
        dataType: "json"
      };
    getValidation(options, checkMark, warningText, validationObject);
  }, 1000)
}


validateParticipantUsername = function() {
  if (this.liveSearchTimer) {
    clearTimeout(this.liveSearchTimer);
  }

  this.liveSearchTimer = setTimeout(function() {
    var userId = $('#participantsDetailsDataWrapper').attr('data-id');
    var validationObject = $('.participantDetailsEditForm .participantUsernameInput');
    var checkMark = $('.participantUsername .checkMark');
    var warningText = $('.participantUsername .warningText');
    var options = {
      url: ApiUrls.validate_participant_username,
      data: {'username': validationObject[0].value, 'userId': userId},
      type: "GET",
      dataType: "json"
    };
    getValidation(options, checkMark, warningText, validationObject);
  }, 1000)
}


getValidation = function(options, checkMark, warningText, validationObject){
    
    options.headers = { 'X-CSRFToken': $.cookie('apros_csrftoken')};
    $.ajax(options)
    .done(function(data) {
      var saveChangeButton = $('.participantDetailsEditForm .participantDetailsSave'); 
      warningText.hide();
      checkMark.hide();
      if(data['status'] == 'notTaken'){
        checkMark.css('display', 'inline');
        checkMark.show();
        validationObject.removeClass('validationError');
        disableSaveChangeButton(saveChangeButton);
      }
      else if(data['status'] == 'taken'){
        warningText.show();
        validationObject.addClass('validationError');
        saveChangeButton.addClass('disabled');
      }
      else if(data['status'] == 'his'){
        warningText.hide();
        checkMark.hide();
        validationObject.removeClass('validationError');
        disableSaveChangeButton(saveChangeButton);
      }
    })
    .fail(function(data) {
      console.log("Ajax failed to fetch data");
    });

}


disableSaveChangeButton = function(saveChangeButton){

  var canSave = true
  $.each($("form").find(':input'), function(i, v){
      if ($(v).hasClass('validationError')){
        canSave = false
      }  
    });
  if (canSave){
    saveChangeButton.removeClass('disabled');
  }

}

InitializeAutocompleteInput = function(url, inputFieldIdentifier)
{
  var options = {
      url: url,
      type: "GET",
      dataType: "json"
    };

  options.headers = { 'X-CSRFToken': $.cookie('apros_csrftoken')};
  $.ajax(options)
  .done(function(data) {
    var selectableList = data.all_items;
    var selectFillList = [] 
    for (var itemIndex=0;itemIndex < selectableList.length; itemIndex++)
    {
      selectFillList.push({value:selectableList[itemIndex].id, label:selectableList[itemIndex].display_name});
    }
    var inputField = $(inputFieldIdentifier);
    inputField.autocomplete({
      minLength: 0,
      source: selectFillList,
      delay: 0,
      select: function( event, ui ) {
        inputField.val( ui.item.label );
        inputField.attr('data-id',ui.item.value);
        return false;
      },
      search: function( event, ui ) {
        var input = $(event.target);
        var source = $(input).autocomplete( "option", "source" );
        var foundMatch = false;
        for (var i=0; i<source.length; i++) {
          if (input.val().trim().toLowerCase() == source[i].label.trim().toLowerCase()){
            foundMatch = true;
            input.attr('data-id', source[i].value);
          }
        }
        if(!foundMatch) {
          input.attr('data-id', '');
        }
      }
      });
  })
  .fail(function(data) {
    console.log("Ajax failed to fetch data");
    console.log(data)
  });
}