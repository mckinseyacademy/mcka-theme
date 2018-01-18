  Apros.views.CompaniesListView = Backbone.View.extend({
    initialize: function(){
      this.collection.fetch({success: function(collection, response, options){
        cloneHeader('#companiesListViewGridBlock');
        collection.getSlowFetchedStatus = true;
        collection.slowFieldsSuccess(collection, response, options);
      }});
    },
    render: function(){
      companiesListViewGrid = new bbGrid.View({
        container: this.$el,
        collection: this.collection,
        enableSearch: true,
        colModel:[
        { title: gettext('Company'), index: true, name: 'name',
          actions: function(id, attributes){ 
            var thisId = attributes['id'];
            var name = attributes['name'];
            if (name)
              return '<a href="/admin/companies/' + thisId + '" target="_self">' + name + '</a>'; 
          } 
        },
        { title: gettext('Company ID'), index: true, name: 'id', sorttype: 'number' },
        { title: gettext('No. of Participants'), index: true, name: 'numberParticipants', sorttype: 'number' },
        { title: gettext('No. of Courses'), index: true, name: 'numberCourses', sorttype: 'number' }
        ]
      });
      var _this = this;
      this.companiesListViewGrid = companiesListViewGrid;
      $(document).on('onClearSearchEvent', { extra : this}, this.onClearSearchEvent);
      $('#companiesCreateNewCompanyButton').on('click','.createNewCompanyOpenModal',function()
      {
        if ($(this).hasClass('disabled'))
          return;
        var create_new_company_modal = '#createNewCompanyModal';
        var create_button = $(create_new_company_modal).find('.createNewCompany');
        var company_name_input = $(create_new_company_modal).find('.companyDisplayName');
        var errorContainer = $(create_new_company_modal).find('.errorMessage');
        $(company_name_input).val('');
        $(errorContainer).empty();
        $(create_button).attr('disabled', 'disabled');
        $(create_button).addClass('disabled');
        $(create_new_company_modal).find('.createNewCompanyControl').find('.closeModal').off().on('click', function()
        {
          $(create_new_company_modal).find('a.close-reveal-modal').trigger('click');
        });
        $(create_new_company_modal).on('keydown','.companyDisplayName',function()
        { 
          $(create_button).attr('disabled', 'disabled');
          $(create_button).addClass('disabled');
        });
        $(create_new_company_modal).on('keyup','.companyDisplayName',function()
        {
          if (_this.liveSearchTimer) 
          {
            clearTimeout(_this.liveSearchTimer);
          }
          _this.liveSearchTimer = setTimeout(function() 
          { 
            var value = $(company_name_input).val().trim();
            if( value != '')
            { 
              if (value.length <= 30)
              {
                var testValue = value.replace(/ /g,'');
                // Todo Internationalization: Company name can only be in english
                if (/^[a-z0-9]+$/i.test(testValue))
                {
                  var url = ApiUrls.company + 'new_company?company_display_name=' + value;
                  var options = {
                    url: url,
                    type: "GET",
                    dataType: "json"
                  };
                  options.headers = { 'X-CSRFToken': $.cookie('apros_csrftoken')};
                  $.ajax(options)
                  .done(function(data) 
                  { 
                    if(data['status'] == 'error')
                    {
                      $(errorContainer).text(data['message']);
                      $(create_button).attr('disabled', 'disabled');
                      $(create_button).addClass('disabled');
                    }
                    else if(data['status'] == 'ok')
                    {
                      $(errorContainer).empty();
                      $(create_button).removeAttr('disabled');
                      $(create_button).removeClass('disabled');
                    }
                  })
                  .fail(function(data) {
                    console.log("Ajax failed to fetch data");
                  });
                }
                else
                {
                  $(errorContainer).text(gettext('This company name cannot contain non-alphanumeric characters!'));
                  $(create_button).attr('disabled', 'disabled');
                  $(create_button).addClass('disabled');
                }
              }
              else
              {
                $(errorContainer).text(gettext('This company name cannot have more than 30 characters!'));
                $(create_button).attr('disabled', 'disabled');
                $(create_button).addClass('disabled');
              }
            }
            else
            {
              $(errorContainer).empty();
              $(create_button).attr('disabled', 'disabled');
              $(create_button).addClass('disabled');
            }
          }, 1000);
        });
        $(create_new_company_modal).on('click','.createNewCompany',function()
        {
          if ($(this).hasClass('disabled'))
            return;
          $(this).attr('disabled', 'disabled');
          $(this).addClass('disabled');
          var company_display_name = $(company_name_input).val().trim();
          var data = {"company_display_name": company_display_name};
          var url = ApiUrls.companies_list + '/new_company';
          var options = {
            url: url,
            data: data,
            type: "POST",
            dataType: "json"
          };
          options.headers = { 'X-CSRFToken': $.cookie('apros_csrftoken')};
          $.ajax(options)
          .done(function(data) {
            if (data['status'] == 'ok')
            {
              location.reload();
            }
            else if (data['status'] == 'error')
            {
              alert(gettext("Couldn't create new company!"))
              return;
            }
          })
          .fail(function(data) {
            console.log("Ajax failed to fetch data");
          });
        });
        $(create_new_company_modal).foundation('reveal', 'open');
      });
    },
    onClearSearchEvent: function(event){
      var _this = event.data.extra;
      _this.companiesListViewGrid.searchBar.onSearch({target: '#mainCompaniesListGridWrapper .bbGrid-pager'});
    },
  });
