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
    $('.clearableParticipantsList').width('170px').change();
});

$(function() {
  $("#program-menu-content").on('opened.fndtn.dropdown', function(e) {
    RecalculateCourseListSize();
  });
  $(window).resize(function() {
    RecalculateCourseListSize();
  });
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
        selectableList[itemIndex].display_name = gettext("NoName");
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
      timeout: 10000,
      beforeSend: function( xhr ) {
        xhr.setRequestHeader("X-CSRFToken", $.cookie('apros_csrftoken'));
      }
    };
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
      contentType: "application/json; charset=utf-8",
      dataType: "json",
      timeout: 10000,
      data: JSON.stringify({"ids":list_of_company_ids}),
      processData: false,  
      beforeSend: function( xhr ) {
        xhr.setRequestHeader("X-CSRFToken", $.cookie('apros_csrftoken'));
      }
    };

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
    contentType: "application/json; charset=utf-8",  
    data: JSON.stringify(dictionaryToSend),
    processData: false,
    type: "POST",
    dataType: "json",  
    beforeSend: function( xhr ) {
      xhr.setRequestHeader("X-CSRFToken", $.cookie('apros_csrftoken'));
    }
  };
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
  
  if(args.header) {
      result += keys.join(columnDelimiter);
      result += lineDelimiter;
  }

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
      data: args.data,
      header: 'header' in args? args.header: true // by-default header row is always written
  });
  if (csv == null) return;
  filename = args.filename || 'export.csv';

  // encodeURIComponent can encode more characters than encodeURI
  // works for FF as well
  var csvData = encodeURIComponent(csv);

  if (!csv.match(/^data:text\/csv/i)) {
      csvData = 'data:text/csv;charset=utf-8,' + csvData;
  }

  link = document.createElement('a');
  link.setAttribute('href', csvData);
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}


function CreateNicePopup(title, content, customClass)
{
  if (!customClass)
    customClass = "";
  popup_html = "<div class='fixedDynamicPopupContainer reveal-modal small "+customClass+"' style='display:block; visibility:visible;'>";
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
  content += '<br><input type="text"/><div class="button savePromptChanges disabled">'+gettext('Send')+'</div>';
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

function CreateNiceAjaxLinkList(parent_container, resource_name, hrefPrefix, urlParams)
{
  $(parent_container).empty();
  $(parent_container).append('<i class="fa fa-spinner fa-spin"></i>');
  if (!hrefPrefix)
    hrefPrefix=""
  var options = {
    url: ApiUrls.cached_resource_api(resource_name),
    type: "GET",
    dataType: "json",    
    data: urlParams,
    timeout: 1000000,
    beforeSend: function( xhr ) {
      xhr.setRequestHeader("X-CSRFToken", $.cookie('apros_csrftoken'));
    }
  };
  $.ajax(options)
  .done(function(data) {
    var link_list = '';
    for (var i=0; i<data.length; i++)
    {
      link_list += '<a href="'+hrefPrefix+data[i]["value"]+'" class="resourceName_'+resource_name+'" style="display:block;">'+data[i]["name"]+'</a>';
    }
    link_list += "";
    $(parent_container).empty();
    $(parent_container).append(link_list);
    $(document).trigger("nice_links_generated", [parent_container]);
  })
  .fail(function(data) {
    console.log("Ajax failed to fetch data");
    console.log(data)
  });
}


function CreateNiceAjaxSelect(parent_container, resource_name, select_data, default_option, urlParams)
{
  $(parent_container).empty();
  $(parent_container).append('<i class="fa fa-spinner fa-spin"></i>');
  var options = {
    url: ApiUrls.cached_resource_api(resource_name),
    type: "GET",
    dataType: "json",
    data: urlParams,
    timeout: 1000000,
    beforeSend: function( xhr ) {
      xhr.setRequestHeader("X-CSRFToken", $.cookie('apros_csrftoken'));
    }
  };
  $.ajax(options)
  .done(function(data) {
    if (!select_data["customAttr"])
      select_data["customAttr"]="";
    var select_html = '<select class="niceAjaxSelectGlobal resourceName_'+resource_name+'" id="'+select_data["id"]+'" name="'+select_data["name"]+'" '+select_data["customAttr"]+'>';
    if (default_option){
      if (!default_option["customAttr"])
        default_option["customAttr"]="";
      select_html += '<option value="'+default_option["value"]+'" '+default_option["customAttr"]+'>'+default_option["name"]+'</option>';
    }
    for (var i=0; i<data.length; i++)
    {
      select_html += '<option value="'+data[i]["value"]+'">'+data[i]["name"]+'('+data[i]['value']+')</option>';
    }
    select_html += "</select>";
    $(parent_container).empty();
    $(parent_container).append(select_html);
    $(document).trigger("nice_select_generated", [parent_container]);
  })
  .fail(function(data) {
    console.log("Ajax failed to fetch data");
    console.log(data)
  });
}

function CreateNiceAjaxTemplate(parent_container, resource_name, render_data, urlParams)
{
  $(parent_container).empty();
  $(parent_container).append('<i class="fa fa-spinner fa-spin"></i>');
  var options = {
    url: ApiUrls.cached_resource_api(resource_name),
    type: "GET",
    dataType: "json",
    data: urlParams,
    timeout: 1000000,
    beforeSend: function( xhr ) {
      xhr.setRequestHeader("X-CSRFToken", $.cookie('apros_csrftoken'));
    }
  };
  $.ajax(options)
  .done(function(data) {

    var templ = _.template(render_data["template"]);
    var data_extended = {};
    var html = "";

    if (render_data["render_prefix"])
      html += render_data["render_prefix"];

    if (render_data["default"])
      html += templ(render_data["default"]);

    for (var i=0; i<data.length; i++)
    {
      data_extended = data[i]
      if (render_data["data"])
        data_extended = $.extend({},data[i],render_data["data"]);
      html += templ(data_extended);
    }

    if (render_data["render_postfix"])
      html += render_data["render_postfix"];

    $(parent_container).empty();
    $(parent_container).append(html);
    $(document).trigger("nice_"+render_data["type"]+"_generated", [parent_container]);
  })
  .fail(function(data) {
    console.log("Ajax failed to fetch data");
    console.log(data)
  });
}

function CreateNiceAjaxTable(parent_container, resource_name, table_data, urlParams)
{
  $(parent_container).empty();
  $(parent_container).append('<i class="fa fa-spinner fa-spin"></i>');
  var options = {
    url: ApiUrls.cached_resource_api(resource_name),
    type: "GET",
    dataType: "json",
    data: urlParams,
    timeout: 1000000,
    beforeSend: function( xhr ) {
      xhr.setRequestHeader("X-CSRFToken", $.cookie('apros_csrftoken'));
    }
  };
  $.ajax(options)
  .done(function(data) {
    var table_html = '';
    if (table_data["header_fields"])
    {
      table_html +='<thead><tr>';
      for (var j=0; j<table_data["header_fields"].length; j++)
      {
        table_html += '<th>'+table_data["header_fields"][j]+'</th>';
      }
      table_html +='</tr></thead>';
    }
    table_html += "<tbody>";
    for (var i=0; i<data.length; i++)
    {
      table_html += '<tr id="'+data[i]["row_ids"]+'" class="'+table_data["row_classes"]+" "+data[i]["additional_class"]+'">';
      for (var k=0; k<data[i]["table_data"].length; k++)
       table_html +=' <td>'+data[i]["table_data"][k]+'</td>'
      table_html += '</tr>';
    }
    table_html += "</tbody>";
    $(parent_container).empty();
    $(parent_container).append(table_html);
    $(document).trigger("nice_table_generated", [parent_container]);
  })
  .fail(function(data) {
    console.log("Ajax failed to fetch data");
    console.log(data)
  });
}


function GenerateCSVDownloader(click_element, data_to_send)
{
  if (!data_to_send)
    data_to_send = {"chunk_size":100};
  var options = {
    url: $(click_element).attr("data-url"),
    data: data_to_send,
    type: "POST",
    dataType: "json",  
    beforeSend: function( xhr ) {
      xhr.setRequestHeader("X-CSRFToken", $.cookie('apros_csrftoken'));
    }
  };
  $.ajax(options)
  .done(function(data) {
    if (data['status'] == 'csv_task_created')
    {
      var customClass = $(click_element).attr("data-custom-class");
      if (!customClass)
        customClass = "";
      var fileName = {'file_name': data['file_name']};
      var fileNameStr = gettext("Fetching data for file: %(filename)s");
      var title = interpolate(fileNameStr, fileName, true);
      var content = "<progress style='width:100%', value='0' max='"+data["chunk_count"]+"'></progress>";
      CreateNicePopup(title, content, customClass);
      var data_send = {"task_id":data["task_id"], "chunk_request":0};
      GenerateCSVDownloader(click_element, data_send)
    }
    else if (data['status'] == 'csv_chunk_sent')
    {
      var customClass = $(click_element).attr("data-custom-class");
      if (customClass)
      {
        var popup_progress = $("."+customClass).find("progress");
        popup_progress.attr('value', data["chunk_request"]);
        $(document).trigger("csv_chunk_sent", [data]);
        if (data["chunk_request"] < data["chunk_count"])
        {
          var data_send = {"task_id":data["task_id"], "chunk_request":data["chunk_request"]};
          GenerateCSVDownloader(click_element, data_send);
        }
      }
    }
    else if (data['status'] == 'error')
    {
      alert(data["message"]);
    }
  })
  .fail(function(data) {
    console.log("Ajax failed to fetch data");
    console.log(data);
  })
}

function CSVDataCollector(event,data)
{
  if (typeof CSVDataCollector[data["task_id"]] === "undefined")
  {
    CSVDataCollector[data["task_id"]] = {};
    CSVDataCollector[data["task_id"]]["data"] = data["data"];
    CSVDataCollector[data["task_id"]]["filename"] = data["file_name"];
    if (data["chunk_request"] === data["chunk_count"])
    {
      downloadCSV(CSVDataCollector[data["task_id"]]);
      setTimeout(function()
      {
        delete CSVDataCollector[data["task_id"]];
      }, 30000);
    }
  }
  else
  {
    if (data["chunk_request"] < data["chunk_count"])
    {
      CSVDataCollector[data["task_id"]]["data"] = CSVDataCollector[data["task_id"]]["data"].concat(data["data"]);
    }
    else
    {
      CSVDataCollector[data["task_id"]]["data"] = CSVDataCollector[data["task_id"]]["data"].concat(data["data"]);
      downloadCSV(CSVDataCollector[data["task_id"]]);
      setTimeout(function()
      {
        delete CSVDataCollector[data["task_id"]];
      }, 30000);
    }
  }
}

function S3FileUploader(files){
  var formData = new FormData();
  for (var i = 0; i < files.length; i++) {
    var file = files[i];
    // Add the file to the request.
    formData.append('files[]', file, file.name);
  }
  var options = {
      url: ApiUrls.file_upload,
      type: "POST",
      timeout: 10000,
      processData: false,
      contentType: false,
      data: formData,
      beforeSend: function( xhr ) {
        xhr.setRequestHeader("X-CSRFToken", $.cookie('apros_csrftoken'));
      }
    };

  $.ajax(options)
  .done(function(data) {
    $(document).trigger('s3_files_uploaded', [data]);
  })
  .fail(function(data) {
    $(document).trigger('s3_files_failed', [data]);
    console.log("Ajax failed to fetch data");
    console.log(data)
  });
}

function RecalculateCourseListSize(){
  var course_list = $("#program-menu-content");
  if (course_list.hasClass("open"))
  {
    var course_list_height = parseInt(course_list.height());
    var top_offset = parseInt(course_list.offset().top);
    var window_height = parseInt($("html").height());
    if (window_height < course_list_height+top_offset)
    {
      setTimeout(function(){course_list.css({"height": window_height-top_offset+"px", "overflow":"auto"})}, 50);
    }
  }
}

function InternationalizePercentage(value){
    var textTemplate = gettext('%(value)s%');
    var templateContext = {"value": value.toString()};
    return interpolate(textTemplate, templateContext, true);
}


// Language bar
$(document).ready(function () {
    $('.select-box').click(function () {
        $(this).toggleClass("is-open");
    });

    var currentLanguage = $('a.selected', '.language-selector').text();
    $('span.current_language').html(currentLanguage);

});


function InitializeAverageCalculate() {
  var totalProgress = 0;
  var totalProficiency = 0;
  var total = 0;
  // Progressbar for progress column
  var dataTarget = $("a.hashPageButton.active").attr('data-target');
  $('.'+dataTarget+' td.progress span').each(function () {
    var text = $(this).text();
    $(this).css("width" , text);
    totalProgress += parseInt(text.replace("%", ""));
    total++;
  });
   $('.'+dataTarget+' td.proficiency').each(function () {
    var text = $(this).text();
    $(this).css("width" , text);
    totalProficiency += parseInt(text.replace("%", ""));
  });

  // Set the Average progess and proficiency	// remove existing subgrid for manager team
  if(total) {
    $('.progress-average large').text(Math.round(totalProgress / total) + "%");
    $('.proficiency-average large span').text(Math.round(totalProficiency / total)+ "%");
  }
  else{
    $('.progress-average large').text("0%");
    $('.proficiency-average large span').text("0%");
  }
}

// remove existing subgrid for manager team
function RemoveExistingSubGird(element) {
  // check if already subgrid is loaded for some other record
  var checkSubGrid = $("tr.bbSubGrid");
  if(checkSubGrid){
    // if it exists, trigger click from tr
    // its needed to close the any other opened subgrid
    $(element).parent().click();
  }
}
