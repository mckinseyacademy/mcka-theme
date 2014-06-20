var _default_success = function(response){
  alert(response.message);
  window.location.reload();
};

var _default_error = function(jqXHR, textStatus, errorThrown){
  var message = textStatus + " - " + errorThrown;
  if(jqXHR.responseJSON){
    message = jqXHR.responseJSON.message;
  }
  else if(jqXHR.responseText){
    message = jqXHR.responseText;
  }
  alert(message);
};

function submit_form_message_response(overlay, formSelector, success_fn, error_fn){
  overlay.on('submit', formSelector, function(e){
    e.preventDefault();
    var form = $(this);

    var on_success = success_fn ? success_fn : _default_success;
    var on_error = error_fn ? error_fn : _default_error;

    $.ajax({
      type: form.attr('method'),
      url: form.attr('action'),
      data: form.serialize(),
      dataType: 'json',
      success: on_success,
      error: on_error
    });
  });
}

function enable_selection(selections, activator){
  var _multi_selection = function(){
    $(this).toggleClass('selected');
  };

  if(!$.isArray(selections)){
    selections = [selections];
  }

  for (var i = 0; i < selections.length; ++i){
    var select_func = _multi_selection;
    var select_class_name = selections[i].class_name ? selections[i].class_name : "selected";
    var select_action = selections[i].select_action ? selections[i].select_action : "click";
    if(selections[i].single_select){
      var use_selector = selections[i].selector;
      select_func = function(){
        $(use_selector).removeClass(select_class_name);
        $(this).addClass(select_class_name);
      };
    }
    $(selections[i].selector).on(select_action, select_func);
  };

  $(activator.selector).on('click', function(event){
    event.preventDefault();

    var data = {};
    for (var i = 0; i < selections.length; ++i){
      var min_count = selections[i].minimum_count ? selections[i].minimum_count : 1;
      var data_selector = selections[i].data_selector ? selections[i].data_selector : "";
      var data_field = selections[i].data_field ? selections[i].data_field : "";
      var these_selections = $(selections[i].selector + "." + select_class_name + data_selector);
      if(these_selections.length < min_count){
        alert(selections[i].minimum_count_message);
        return false;
      }

      var selection_data = [];
      if(data_field != ''){
        these_selections.each(function(index, include_value){
          selection_data.push({'id': include_value.id, data_field: $(include_value).data(data_field)});
        });
      }
      else{
        these_selections.each(function(index, include_value){
          selection_data.push(include_value.id);
        });
      }
      data[selections[i].submit_name] = (selections[i].single_select && data_selector.length == 0) ? selection_data[0] : selection_data;
    };

    var on_success = activator.success ? activator.success : _default_success;
    var on_error = activator.error ? activator.error : _default_error;
    var use_url = activator.submit_url ? activator.submit_url : $(this).attr('href');

    data["csrfmiddlewaretoken"] = $.cookie('apros_csrftoken');
    $.ajax({
      url: use_url,
      type: "POST",
      data: data,
      dataType: 'json',
      success: on_success,
      error: on_error
    });

    return false;
  });
}
