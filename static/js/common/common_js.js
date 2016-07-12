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
      $('#participantsSearchWrapper').find('input').trigger('keyup');
    } } );

    // update value
    $('.clearableParticipantsList').val('').change();
    
    // change width
    $('.clearableParticipantsList').width('200px').change();
});

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
      timeout: 10000
    };

  options.headers = { 'X-CSRFToken': $.cookie('apros_csrftoken')};
  $.ajax(options)
  .done(function(data) {
    var selectableList = data.all_items;
    var selectFillList = [] 
    for (var itemIndex=0;itemIndex < selectableList.length; itemIndex++)
    {
      if (selectableList[itemIndex].display_name == null)
        selectableList[itemIndex].display_name = "NoName";
      selectFillList.push({value:selectableList[itemIndex].id, label:selectableList[itemIndex].display_name});
    }
    thisToAppend[sourceName] = selectFillList;
  })
  .fail(function(data) {
    console.log("Ajax failed to fetch data");
    console.log(data)
  });
}
GetUserAdminCompanies = function(user_id){
  var options = {
      url: ApiUrls.company_admin_get_post_put_delete(user_id),
      type: "GET",
      dataType: "json",
      timeout: 10000
    };

  options.headers = { 'X-CSRFToken': $.cookie('apros_csrftoken')};
  $.ajax(options)
  .done(function(data) {
    $(document).trigger('admin_companies_get', [data])
  })
  .fail(function(data) {
    console.log("Ajax failed to fetch data");
    console.log(data)
  });
}
PutUserAdminCompanies = function(user_id, list_of_company_ids){
  var options = {
      url: ApiUrls.company_admin_get_post_put_delete(user_id),
      type: "PUT",
      dataType: "json",
      timeout: 10000,
      data: JSON.stringify({"ids":list_of_company_ids}),
      processData: false
    };

  options.headers = { 'X-CSRFToken': $.cookie('apros_csrftoken')};
  $.ajax(options)
  .done(function(data) {
    $(document).trigger('admin_companies_put', [data])
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
InitializeTooltipOnPage = function(onClickEnable)
{
    var ID = "tooltip", CLS_ON = "tooltip_ON", FOLLOW = true,
    DATA = "_tooltip", OFFSET_X = 20, OFFSET_Y = 20;
    $("<div id='" + ID + "' style='display: none'/>").appendTo("body");
    var _show_value = "";
    showAt = function (e) {
        var ntop = e.pageY + OFFSET_Y, nleft = e.pageX + OFFSET_X;
        $("#" + ID).text(_show_value).css({
            position: "absolute", top: ntop, left: nleft, 'z-index':20000
        }).show();
    };
    if(onClickEnable)
    {
      var current_element = null;
      $(document).on("click", "*[data-title]:not([data-title=''])", function (e) {
        e.stopPropagation();
        if($(this).hasClass(CLS_ON))
        {
          _show_value = ''
          $(this).removeClass(CLS_ON);
          $("#" + ID).hide();
        } 
        else
        {
          current_element = e.target;
          _show_value = $(this).attr("data-title");
          $(this).addClass(CLS_ON);
          showAt(e);
        }
      });
      $(document).on('click', function (e)
      {
        _show_value = ''
        $(current_element).removeClass(CLS_ON);
        $("#" + ID).hide();
      });
    }
    else
    {
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
SendEmailManager = function(sender, subject, to_email_list, body, template_id, previewEmail, optional_data)
{
  var dictionaryToSend = {'subject':subject, 'from_email': sender, 'to_email_list': to_email_list, 'email_body': body}
  if (template_id)
    dictionaryToSend['template_id'] = template_id;
  if (optional_data)
    dictionaryToSend['optional_data'] = optional_data;
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


function convertArrayOfObjectsToCSV(args) {  
  var result, ctr, keys, columnDelimiter, lineDelimiter, data;

  data = args.data || null;
  if (data == null || !data.length) {
      return null;
  }

  columnDelimiter = args.columnDelimiter || ',';
  lineDelimiter = args.lineDelimiter || '\n';

  keys = Object.keys(data[0]);

  result = '';
  result += keys.join(columnDelimiter);
  result += lineDelimiter;

  data.forEach(function(item) {
      ctr = 0;
      keys.forEach(function(key) {
          if (ctr > 0) result += columnDelimiter;

          result += item[key];
          ctr++;
      });
      result += lineDelimiter;
  });

  return result;
}


function downloadCSV(args) {  
  var data, filename, link;
  var csv = convertArrayOfObjectsToCSV({
      data: args.data
  });
  if (csv == null) return;
  filename = args.filename || 'export.csv';

  if (!csv.match(/^data:text\/csv/i)) {
      csv = 'data:text/csv;charset=utf-8,' + csv;
  }
  data = encodeURI(csv);
  link = document.createElement('a');
  link.setAttribute('href', data);
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}


function CreateNicePopup(title, content)
{
  popup_html = "<div class='fixedDynamicPopupContainer reveal-modal small' style='display:block; visibility:visible;'>";
  if (title)
    popup_html += "<div class='fixedDynamicPopupTitle'>"+title+"</div>";
  popup_html += '<i class="fa fa-times-circle fixedDynamicPopupCancelButton" aria-hidden="true"></i>';
  popup_html += "<hr>";
  if (content)
    popup_html += "<div class='fixedDynamicPopupContent'>"+content+"</div>";
  popup_html += "</div>";
  $("body").append(popup_html);
  popup = $("body").find(".fixedDynamicPopupContainer").last();
  popup.on("click", ".fixedDynamicPopupCancelButton", function(){
    $(this).parents(".fixedDynamicPopupContainer").hide(400, function(){
      $(this).remove();
    })
  })
}

function CreatNicePrompt(title, input_label)
{
  content = '<div class="fixedDynamicPopupPrompContentContainer"><div class="fixedDynamicPopupPrompContent">'+input_label+'</div>';
  content += '<br><input type="text"/><div class="button savePromptChanges disabled">Send</div>';
  content += '</div>';
  var _this = this;
  CreateNicePopup(title, content);
  popup = $("body").find(".fixedDynamicPopupContainer").last();
  popup.on('keyup', 'input', function()
  {
    var _thisInput = $(this);
    if (_this.liveSearchTimer) 
    {
      clearTimeout(_this.liveSearchTimer);
    }
    _this.liveSearchTimer = setTimeout(function() 
    {
      var value = _thisInput.val().trim();
      if (value != '')
      {
        popup.find('.savePromptChanges').removeClass('disabled');
      }
      else
      {
        popup.find('.savePromptChanges').addClass('disabled');
      }
    }, 1000);
  });

  popup.on("click", ".savePromptChanges", function(){
    if ($(this).hasClass('disabled'))
          return;
    data = $(this).parents(".fixedDynamicPopupContainer").find("input").val().trim();
    if (data.length > 0)
    {
      $(document).trigger("dynamic_prompt_confirmed", [data]);
      $(this).parents(".fixedDynamicPopupContainer").hide(400, function(){
        $(this).remove();
      })
    }
  })

}

