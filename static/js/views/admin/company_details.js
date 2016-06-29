  Apros.views.CompanyDetailsCoursesView = Backbone.View.extend({
    initialize: function(){
      this.collection.fetch({success: function(){
        cloneHeader('#companyDetailsCoursesViewGridBlock');
      }});
      this.setEditCompanyNameEvents();
    },
    render: function(){
      companyDetailsCoursesViewGrid = new bbGrid.View({
        container: this.$el,
        collection: this.collection,
        enableSearch: true,
        colModel:[
        { title: 'Course Name', index: true, name: 'name',
          actions: function(id, attributes){ 
            var thisId = attributes['id']
            var name = attributes['name']
            if (name.length > 75){
              return '<a href="/admin/courses/' + thisId + '" target="_self">' + name.slice(0,75) + '...</a>'; 
            }
            return '<a href="/admin/courses/' + thisId + '" target="_self">' + name + '</a>'; 
          } 
        },
        { title: 'Course ID', index: true, name: 'id' },
        { title: 'Participants', index: true, name: 'participants', sorttype: 'number'},
        { title: 'Start', index: true, name: 'start',
          actions: function(id, attributes){ 
            if (attributes['start'] != '-'){
              var start = attributes['start'].split(',')[0].split('/');
              return '' + start[1] + '/' + start[2] + '/' + start[0];
            }
            return attributes['start'];
          } 
        },
        { title: 'End', index: true, name: 'end',
          actions: function(id, attributes){ 
            if (attributes['end'] != '-'){
              var end = attributes['end'].split(',')[0].split('/');
              return '' + end[1] + '/' + end[2] + '/' + end[0];
            }
            return attributes['end'];
          } 
        },
        { title: 'Cohort Comp.', index: true, name: 'cohort' },
        ]
      });
    },
    setEditCompanyNameEvents: function()
    {
      var _this = this;
      var dataContainer = $('#companyDetailsTopDataWrapper');
      var _saved = true;
      dataContainer.on('click', '.editCompanyNameIcon', function()
      {
        _saved = false;
        $('#mainCompanyDetailsDataContainer').find('.errorMessage').empty();
        var mainContainer = $(this).parents('.companyDetailsCompanyName');
        var textContainer = mainContainer.find('.companyDetailsTextName');
        var editContainer = mainContainer.find('.companyDetailsInputName');
        var text_width = textContainer.width();
        editContainer.find('input').val(textContainer.text().trim());
        textContainer.hide();
        mainContainer.find('.editCompanyNameIcon').hide();
        editContainer.find('input').width(text_width);
        editContainer.show();
        editContainer.find('input').focus();
      });
      dataContainer.on('blur', '.companyDetailsInputName input', function()
      {
        if (_saved)
          return;
        _saved = true;
        $('#mainCompanyDetailsDataContainer').find('.errorMessage').empty();
        _this.hideCompanyEditInput(this);
        _this.validateCompanyName($(this).val().trim());
      });
      dataContainer.on('keydown', '.companyDetailsInputName input', function(ev)
      {
        var keycode = (ev.keyCode ? ev.keyCode : ev.which);
        if(keycode == 13) 
        {
          if (_saved)
            return
          _saved = true;
          $('#mainCompanyDetailsDataContainer').find('.errorMessage').empty();
          _this.hideCompanyEditInput(this);
          _this.validateCompanyName($(this).val().trim());
        }
      });
    },
    hideCompanyEditInput: function(eventElement){
      var mainContainer = $(eventElement).parents('.companyDetailsCompanyName');
      var textContainer = mainContainer.find('.companyDetailsTextName');
      var editContainer = mainContainer.find('.companyDetailsInputName');
      textContainer.show();
      mainContainer.find('.editCompanyNameIcon').show();
      editContainer.hide();
    },
    validateCompanyName: function(newName)
    {
      if(newName != '') 
      {
        var testValue = newName.replace(/ /g,'');
        if (/^[a-z0-9]+$/i.test(testValue)) 
        {
          var _this = this;
          var companyId = $("#mainCompanyDetailsDataContainer").attr("data-id");
          var options = {
            url: ApiUrls.company+companyId+"/edit?company_display_name=" + newName,
            type: "GET",
            dataType: "json"
          };
          options.headers = { 'X-CSRFToken': $.cookie('apros_csrftoken')};
          $.ajax(options)
          .done(function(data) 
          {
            if (data['status'] == 'ok')
            {
              _this.updateCompanyName(newName);
            }
            else if(data['status'] == 'error')
            {
              $('#mainCompanyDetailsDataContainer').find('.errorMessage').text(data['message']);
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
        else
        {
          $('#mainCompanyDetailsDataContainer').find('.errorMessage').text('This company name cannot contain non-alphanumeric characters!');
        }
      }
      else
      {
        $('#mainCompanyDetailsDataContainer').find('.errorMessage').text('No Company Display Name!');
      }
    },
    updateCompanyName: function(newName)
    {
      var _this = this;
      var companyId = $("#mainCompanyDetailsDataContainer").attr("data-id");
      var data = {"display_name": newName};
      var options = {
        url: ApiUrls.company+companyId+"/edit",
        data: data,
        type: "POST",
        dataType: "json"
      };
      options.headers = { 'X-CSRFToken': $.cookie('apros_csrftoken')};
      $.ajax(options)
      .done(function(data) {
        if (data['status'] == 'ok')
        {
          var mainContainer = $("#companyDetailsTopDataWrapper");
          var newCompanyName = mainContainer.find('.companyDetailsInputName input').val().trim();
          mainContainer.find('.companyDetailsTextName').text(newCompanyName);
        }
        alert(data['message']);
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
  });