  Apros.views.CompanyLinkedAppsView = Backbone.View.extend({
    gridColumns:
    [
        { title: 'App Name', index: true, name: 'name',
          actions: function(id, attributes){
            var company_id = $('#mainCompanyDetailsDataContainer').attr('data-id');
            var thisId = attributes['id']
            var name = attributes['name']
            if (name){
              if (name.length > 75){
                return '<a href="/admin/companies/' + company_id + '/linkedapps/' + thisId + '" target="_self">' + name.slice(0,75) + '...</a>';
              }
              else
              {
                return '<a href="/admin/companies/' + company_id + '/linkedapps/' + thisId + '" target="_self">' + name + '</a>';
              }
            }
          }
        },
        { title: 'Deployment Mech', index: false, name: 'deployment_mechanism' },
        { title: 'iOS DL URL', index: false, name: 'ios_download_url',
          actions: function(id, attributes){
            return '<a href=' + encodeURIComponent(attributes['ios_download_url']) + '>' + attributes['ios_download_url'] + '</a>';
          }
        },
        { title: 'Android DL URL', index: false, name: 'android_download_url',
          actions: function(id, attributes){
            return '<a href=' + encodeURIComponent(attributes['android_download_url']) + '>' + attributes['android_download_url'] + '</a>';
          }
        },
        { title: 'Urban Airship URL', index: false, name: 'provider_dashboard_url',
          actions: function(id, attributes){
            return '<a href=' + encodeURIComponent(attributes['provider_dashboard_url']) + '>' + attributes['provider_dashboard_url'] + '</a>';
          }
        },
        { title: 'Analytics URL', index: false, name: 'analytics_url',
          actions: function(id, attributes){
            return '<a href=' + encodeURIComponent(attributes['analytics_url']) + '>' + attributes['analytics_url'] + '</a>';
          }
        },
        { title: 'Active', index: false, name: 'is_active',
          actions: function(id, attributes){
            if (attributes['is_active']){
              return '<i class="fa fa-check" aria-hidden="true"></i>';
            }
            else{
              return '<i class="fa fa-close" aria-hidden="true"></i>';
            }
          }
        },
    ],

    initialize: function(){
      this.collection.fetch();
    },
    render: function(){
      var _this = this;
      companyLinkedAppsViewGrid = new bbGrid.View({
        container: this.$el,
        collection: this.collection,
        enableSearch: true,
        colModel: _this.gridColumns
      });
      $(document).on('onClearSearchEvent', this.onClearSearchEvent);

      $('#addAppPopupLink').click(function()
      {
        var mobileapps_container = $('#linkApp');
        var errorMessage = mobileapps_container.find('.errorMessage');
        var linkAppButton = mobileapps_container.find('.linkAppButton');
        var appSearchInput = mobileapps_container.find('#appSearchInput');
        errorMessage.empty();
        linkAppButton.addClass('disabled');
        appSearchInput.val('');
        if(!_this.mobileappsFetched)
        {
          var url = ApiUrls.mobileapps;
          _this.initializeAutocompleteInput(url, '#appSearchInput');
          _this.mobileappsFetched = true;
        }

      });

      $('#linkApp').on('click', '.linkAppButton', function()
      {
        if ($(this).hasClass('disabled'))
          return;
        $(this).addClass('disabled');
        if ($('#appSearchInput').attr('data-id'))
        {
          var appId = $('#appSearchInput').attr('data-id');
          var companyId = $('#mainCompanyDetailsDataContainer').attr('data-id');

          _this.linkAppToCompany(appId, companyId);
        }
      });

      $(document).on('autocomplete_found', function(event, input)
      {
        if (input.parent().is('#linkApp'))
        {
          $('.linkAppButton').removeClass('disabled');
        }
      });
    },
    onClearSearchEvent: function(){
      companyLinkedAppsViewGrid.searchBar.onSearch({target: '#companyDetailsDataWrapper .bbGrid-pager'});
    },
    linkAppToCompany: function(appId, companyId)
    {
      var params = {"app_id": appId};
      var url = ApiUrls.companies_list+'/'+companyId+'/linkedapps';
      var request = {
        url: url,
        data: JSON.stringify(params),
        type: "post",
        contentType: "application/json",
        dataType: 'json'
      };
      request.headers = { 'X-CSRFToken': $.cookie('apros_csrftoken')};
      $.ajax(request)
      .done(function(data) {
        if (data['status'] == 'ok')
        {
          var url = ApiUrls.mobileapps +'/'+appId;
          var options = {
              url: url,
              type: "GET",
              dataType: "json"
            };

          options.headers = { 'X-CSRFToken': $.cookie('apros_csrftoken')};
          $.ajax(options)
          .done(function(data) {
            var mobileapp = data;
            mobileapp = Apros.utils.cleanProps(mobileapp, Apros.config.MOBILEAPP_PROPERTIES_TO_CLEAN);
            companyLinkedAppsViewGrid.collection.add(mobileapp);
          })
          .fail(function(data) {
            console.log("Ajax failed to fetch data");
            console.log(data)
          });
          $('#linkApp').find('a.close-reveal-modal').trigger('click');
        }
        else if (data['status'] == 'error')
        {
          alert("Couldn't link this App!");
          return;
        }
      })
      .fail(function(data) {
        console.log("Ajax failed to fetch data");
      });

    },
    initializeAutocompleteInput: function(url, inputFieldIdentifier)
    {
      var options = {
          url: url,
          type: "GET",
          dataType: "json"
        };

      options.headers = { 'X-CSRFToken': $.cookie('apros_csrftoken')};
      $.ajax(options)
      .done(function(data) {
        var selectableList = data.results;
        var selectFillList = [];
        for (var itemIndex=0;itemIndex < selectableList.length; itemIndex++)
        {
          selectFillList.push({value:selectableList[itemIndex].id, label:selectableList[itemIndex].name});
        }
        GenerateAutocompleteInput(selectFillList, inputFieldIdentifier);
      })
      .fail(function(data) {
        console.log("Ajax failed to fetch data");
        console.log(data)
      });
    },
  });
