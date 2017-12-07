  Apros.views.CompanyMobileappDetails = Backbone.View.extend({
    initialize: function(){
      this.setEditAppNameEvents();
    },
    render: function(){
      var _this = this;

      $('#delinkAppButton').click(function(){
        $('#delinkAppButton').addClass('disabled');
        var companyId = $('#mainCompanyDetailsDataContainer').attr('data-id');
        var url = ApiUrls.companies_list+'/'+companyId+'/linkedapps';

        var app_id = $('#delinkAppButton').attr('data-id')
        params = {"app_id": app_id}
        var request = {
          url: url,
          data: JSON.stringify(params),
          type: "DELETE",
          contentType: "application/json",
          dataType: 'json'
        };
        request.headers = { 'X-CSRFToken': $.cookie('apros_csrftoken')};
        $.ajax(request)
        .done(function(data) {
        if (data['status'] == 'ok')
        {
          $('.backLink')[0].click();
        }
        else if (data['status'] == 'error')
        {
          alert("Couldn't delink App!");
          $('#delinkAppButton').removeClass('disabled');
          return;
        }
        })
        .fail(function(data) {
          $('#delinkAppButton').removeClass('disabled');
          console.log("Ajax failed to fetch data");
        });


      });
    },
    setEditAppNameEvents: function()
    {
      var _this = this;
      var dataContainer = $('#appDetailsTopDataWrapper');
      var _saved = true;
      dataContainer.on('click', '.editAppNameIcon', function()
      {
        _saved = false;
        $('#mainAppDetailsDataContainer').find('.errorMessage').empty();
        var mainContainer = $(this).parents('.appDetailsAppName');
        var textContainer = mainContainer.find('.appDetailsTextName');
        var editContainer = mainContainer.find('.appDetailsInputName');
        var text_width = textContainer.width();
        editContainer.find('input').val(textContainer.text().trim());
        textContainer.hide();
        mainContainer.find('.editAppNameIcon').hide();
        editContainer.find('input').width(text_width);
        editContainer.show();
        editContainer.find('input').focus();
      });
      dataContainer.on('blur', '.appDetailsInputName input', function()
      {
        if (_saved)
          return;
        _saved = true;
        $('#mainAppDetailsDataContainer').find('.errorMessage').empty();
        _this.hideAppEditInput(this);
        _this.validateAppName($(this).val().trim());
      });
      dataContainer.on('keydown', '.appDetailsInputName input', function(ev)
      {
        var keycode = (ev.keyCode ? ev.keyCode : ev.which);
        if(keycode == 13)
        {
          if (_saved)
            return
          _saved = true;
          $('#mainAppDetailsDataContainer').find('.errorMessage').empty();
          _this.hideAppEditInput(this);
          _this.validateAppName($(this).val().trim());
        }
      });
    },
    hideAppEditInput: function(eventElement){
      var mainContainer = $(eventElement).parents('.appDetailsAppName');
      var textContainer = mainContainer.find('.appDetailsTextName');
      var editContainer = mainContainer.find('.appDetailsInputName');
      textContainer.show();
      mainContainer.find('.editAppNameIcon').show();
      editContainer.hide();
    },
    validateAppName: function(newName)
    {
      if(newName != '')
      {
        var testValue = newName.replace(/ /g,'');
        if (/^[a-z0-9]+$/i.test(testValue))
        {
          if (newName.length <= 30)
          {
            this.updateAppName(newName);
          }
          else
          {
            $('#mainAppDetailsDataContainer').find('.errorMessage').text('This app name cannot have more than 30 characters!');
          }
        }
        else
        {
          $('#mainAppDetailsDataContainer').find('.errorMessage').text('This app name cannot contain non-alphanumeric characters!');
        }
      }
      else
      {
        $('#mainAppDetailsDataContainer').find('.errorMessage').text('No App Display Name!');
      }
    },
    updateAppName: function(newName)
    {
      var _this = this;
      var appId = $("#mainAppDetailsDataContainer").attr("data-id");
      var data = {"name": newName};
      var options = {
        url: ApiUrls.mobileapps+'/'+appId,
        data: JSON.stringify(data),
        type: "PUT",
        dataType: "json",
        contentType: "application/json",
      };
      options.headers = { 'X-CSRFToken': $.cookie('apros_csrftoken')};
      $.ajax(options)
      .done(function(data) {
        if (data['status'] == 'ok')
        {
          var mainContainer = $("#appDetailsTopDataWrapper");
          var newAppName = mainContainer.find('.appDetailsInputName input').val().trim();
          mainContainer.find('.appDetailsTextName').text(newAppName);

        }
        })
      .fail(function(data) {
        console.log("Ajax failed to fetch data");
        console.log(data);
        })
    }
  });
