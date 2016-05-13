  Apros.views.CompanyDetailsCoursesView = Backbone.View.extend({
    initialize: function(){
      this.collection.fetch();
      this.setEditCompanyNameEvents();
    },
    render: function(){
      companyDetailsCoursesViewGrid = new bbGrid.View({
        container: this.$el,
        collection: this.collection,
        colModel:[
        { title: 'Course Name', index: true, name: 'name' },
        { title: 'Course ID', index: true, name: 'id' },
        { title: 'Program', index: true, name: 'program' },
        { title: 'Type', index: true, name: 'type' },
        { title: 'Config.', index: true, name: 'configuration' },
        { title: 'Participants', index: true, name: 'participants' },
        { title: 'Start', index: true, name: 'start' },
        { title: 'End', index: true, name: 'end' },
        { title: 'Cohort Comp.', index: true, name: 'cohort' },
        ]
      });
    },
    setEditCompanyNameEvents: function()
    {
      var _this = this;
      var dataContainer = $('#companyDetailsTopDataWrapper');
      dataContainer.on('click', '.editCompanyNameIcon', function()
      {
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
        _this.hideCompanyEditInput(this);
        _this.updateCompanyName($(this).val());
      });
      dataContainer.on('keydown', '.companyDetailsInputName input', function(ev)
      {
        var keycode = (ev.keyCode ? ev.keyCode : ev.which);
        if(keycode == 13) 
        {
          _this.hideCompanyEditInput(this);
          _this.updateCompanyName($(this).val());
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