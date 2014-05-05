function enable_selection(selections, activator){
  var _multi_selection = function(){
    $(this).toggleClass('selected');
  };

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
      var these_selections = $(selections[i].selector + "." + select_class_name + data_selector);
      if(these_selections.length < min_count){
        alert(selections[i].minimum_count_message);
        return false;
      }

      var selection_data = [];
      these_selections.each(function(index, include_value){
        selection_data.push(include_value.id);
      });
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
