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
  var validationObject = $('.participantDetailsEditForm .participantEmailInput');
  var checkMark = $('.participantEmail .checkMark');
  if (SimpleEmailClientValidation(validationObject[0].value))
  {
    this.liveSearchTimer = setTimeout(function() {
      var userId = $('#participantsDetailsDataWrapper').attr('data-id');
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
  else
  {
    checkMark.hide();
  }
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
    GenerateAutocompleteInput(selectFillList, inputFieldIdentifier);
  })
  .fail(function(data) {
    console.log("Ajax failed to fetch data");
    console.log(data)
  });
}

GetAutocompleteSource = function(url, thisToAppend, sourceName){
  var options = {
      url: url,
      type: "GET",
      dataType: "json",
      timeout: 5000
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
    thisToAppend[sourceName] = selectFillList;
  })
  .fail(function(data) {
    console.log("Ajax failed to fetch data");
    console.log(data)
  });
}
GenerateAutocompleteInput = function(source, input)
{
  var inputField = $(input);
  inputField.autocomplete({
    minLength: 0,
    source: function(request, response) {
      var returnArray = [];
      var searchTerm = request.term.toString().trim().toLowerCase();
      $(source).each(function(i,v){
        if ((v.label.toString().trim().toLowerCase().lastIndexOf(searchTerm) > -1) || (v.value.toString().trim().toLowerCase().lastIndexOf(searchTerm) > -1))
        {
          returnArray.push(v);
        }
      });
      response(returnArray);
    },
    select: function( event, ui ) {
        inputField.val( ui.item.label );
        inputField.attr('data-id',ui.item.value);
        inputField.parent().find('.correctInput').show();
        $(document).trigger('autocomplete_found', [inputField])
        return false;
      },
    search: function( event, ui ) {
        var input = $(event.target);
        var inputVal = input.val().trim().toLowerCase();
        var foundMatch = false;
        for (var i=0; i<source.length; i++) {
          if ((inputVal == source[i].label.trim().toLowerCase()) || (inputVal == source[i].value.toString().trim().toLowerCase())){
            foundMatch = true;
            input.attr('data-id', source[i].value);
            input.parent().find('.correctInput').show();
            $(document).trigger('autocomplete_found', [input])
          }
        }
        if(!foundMatch) {
          input.attr('data-id', '');
          input.parent().find('.correctInput').hide();
          $(document).trigger('autocomplete_not_found', [input])
        }
      }
    });
  inputField.on( "focus", function( event, ui ) {
    $(event.target).trigger('keydown');
  });
  return inputField;
}

function RecursiveJsonToHtml( data ) {
  var htmlRetStr = "<ul class='recurseObj' >";
  for (var key in data) {
        if (typeof(data[key])== 'object' && data[key] != null) {
            htmlRetStr += "<li class='keyObj' ><strong>" + key + ":</strong><ul class='recurseSubObj' >";
            htmlRetStr += RecursiveJsonToHtml( data[key] );
            htmlRetStr += '</ul  ></li   >';
        } else {
            htmlRetStr += ("<li class='keyStr' ><strong>" + key + ': </strong>&quot;' + data[key] + '&quot;</li  >' );
        }
  };
  htmlRetStr += '</ul >';    
  return( htmlRetStr );
}
InitializeTooltipOnPage = function()
{
    var ID = "tooltip", CLS_ON = "tooltip_ON", FOLLOW = true,
    DATA = "_tooltip", OFFSET_X = 20, OFFSET_Y = 20 - parseInt($('body').css('top'));
    $("<div id='" + ID + "' style='display: none'/>").appendTo("body");
    var _show_value = "";
    showAt = function (e) {
        var ntop = e.pageY + OFFSET_Y, nleft = e.pageX + OFFSET_X;
        $("#" + ID).text(_show_value).css({
            position: "absolute", top: ntop, left: nleft, 'z-index':20000
        }).show();
    };
    $(document).on("mouseenter", "*[data-title]:not([data-title=''])", function (e) {
        _show_value = $(this).attr("data-title");
        $(this).addClass(CLS_ON);
        showAt(e);
    });
    $(document).on("mouseleave", "." + CLS_ON, function (e) {
        _show_value = ''
        $(this).removeClass(CLS_ON);
        $("#" + ID).hide();
    });
    if (FOLLOW) { $(document).on("mousemove", "." + CLS_ON, showAt); }
}

EmailTemplatesManager = function(method, pk, title, subject, body)
{
  var options = {
    url: ApiUrls.email_templates,
    type: method,
    dataType: "json",
    timeout: 5000
  };
  if ((method == 'POST') || (method == 'PUT'))
  {
    options.data = {'subject': subject, 'title':title, 'body':body};
    if (method == 'PUT')
      options.data['pk'] = pk;     
  }
  if ((method == 'PUT') || (method == 'DELETE'))
  {
    options.url += '/' + pk;
  }
  options.headers = { 'X-CSRFToken': $.cookie('apros_csrftoken')};
  $.ajax(options)
    .done(function(data) {
      if (method == 'GET')
        $(document).trigger('email_templates_fetched', [{'data':data}]);
      else if (data['status'] = 'ok')
      {
        if (method == 'DELETE')
        {
          $(document).trigger('email_template_deleted', [{'pk':pk}]);
        }
        else if (method == 'PUT')
        {
          $(document).trigger('email_template_updated', [{'data':data['data']}]);
        }
        else if (method == 'POST')
        {
          $(document).trigger('email_template_added', [{'data':data['data']}]);
        }
      }
    })
    .fail(function(data) {
      console.log("Ajax failed to fetch data");
      console.log(data)
    })
    .always(function(data)
    {
      $(document).trigger('email_template_finished', [data]);
    })
}
SendEmailManager = function(sender, subject, to_email_list, body, template_id, previewEmail)
{
  var dictionaryToSend = {'subject':subject, 'from_email': sender, 'to_email_list': to_email_list, 'email_body': body}
  if (template_id)
    dictionaryToSend['template_id'] = template_id;
  var options = {
    url: ApiUrls.email,
    data: JSON.stringify(dictionaryToSend),
    processData: false,
    type: "POST",
    dataType: "json"
  };
  options.headers = { 'X-CSRFToken': $.cookie('apros_csrftoken')};
  $.ajax(options)
  .done(function(data) {
    if (data['status'] == 'ok')
    {
      data['type']= 'email';
      if (previewEmail)
        data['type']='preview';
      $(document).trigger('email_sent', [data]);
    }
    })
  .fail(function(data) {
    console.log("Ajax failed to fetch data");
    console.log(data);
    })
  .always(function(data)
  {
    $(document).trigger('email_finished', [data]);
  })
}

function SimpleEmailClientValidation(emailAddress) {
    var pattern = new RegExp(/^[+a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/i);
    return pattern.test(emailAddress);
};