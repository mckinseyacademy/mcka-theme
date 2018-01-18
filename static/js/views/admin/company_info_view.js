  Apros.views.CompanyInfoView = Backbone.View.extend({
    initialize: function(){
      var _this = this;
      InitializeTooltipOnPage(true);
      var invoicingDetailsContainer = $('#companyInfoInvoicingDetailsData');
      var contactsWrapper = $('#companyInfoContacts');
      var contactsContainers = contactsWrapper.find('.companyInfoContactsData');
      var invoicingDetailsEditContainer = $('#companyInfoInvoicingDetailsEdit');
      var contactsEditContainer = contactsWrapper.find('.companyInfoContactsEdit');
      var invoicingDetailsEditButton = $('#companyInfoInvoicingDetails .companyInvoicingDetailsEditButton');
      var contactsEditButton = contactsWrapper.find('.companyContactsEditButton');
      var invoicingDetailsSaveButton = invoicingDetailsEditContainer.find('.invoicingDetailsSaveButton');
      var contactsSaveButton = contactsWrapper.find('.contactsSaveButton');

      $('#country_edit').countrySelect();
      var name = $('#country_edit').attr('data-country-long');
      var selectableCountries = $.fn['countrySelect'].getCountryData();
      for (var i = 0; i<selectableCountries.length;i++)
      { 
        if (selectableCountries[i].name == name)
        {
          $('.countryText').text(name);
          $("#country_edit").countrySelect("selectCountry", selectableCountries[i].iso2);
          break;
        }  
      }

      invoicingDetailsEditContainer.hide();
      contactsEditContainer.hide();

      invoicingDetailsEditButton.off().on("click", function(){
        $(this).hide();
        invoicingDetailsContainer.hide();
        invoicingDetailsEditContainer.show();
      });

      contactsEditButton.off().on("click", function(){
        $(this).hide();
        contactsContainers.hide();
        contactsEditContainer.show();
      });

      invoicingDetailsEditContainer.find('.invoicingDetailsCancelEdit').off().on("click", function(){
        var flag = 'invoicing';
        _this.refreshData(flag);
      });

      contactsWrapper.find('.contactsCancelEdit').off().on("click", function(){
        var flag = 'contacts';
        _this.refreshData(flag);
      });

      invoicingDetailsEditContainer.find('input').off('focus').on('focus', function(){
        invoicingDetailsSaveButton.removeClass('disabled');
      });

      contactsEditContainer.find('input').off('focus').on('focus', function(){
        contactsSaveButton.removeClass('disabled');
      });

      invoicingDetailsSaveButton.off().on('click', function(){
        var flag = 'invoicing';
        var data = {};
        data['flag'] = flag;
        data['invoicing'] = [];
        var item = {};
        $.each(invoicingDetailsEditContainer.find(':input'), function(i, v){
          var input = $(v);
          item[input.attr("name")] = input.val().trim();  
        });
        data['invoicing'].push(item);
        _this.putData(_this, data, flag);
        $(this).addClass('disabled');
      });

      contactsSaveButton.off().on('click', function(){
        var flag = 'contacts';
        var data = {};
        data['flag'] = flag;
        data['contacts'] = [];
        var contactsRows = $('#companyInfoContacts').find('.companyContactsRow');
        contactsRows.each(function (index, value){
          var item = {};
          var _this = this;
          var contactType = $(_this).find('.contactTypeText');
          var contactId = $(_this).find('.contactTypeRow').attr('data-id');
          item['type'] = contactType.text();
          item['type_id'] = contactId;
          $.each($(_this).find(':input'), function(i, v){
            var input = $(v);
            item[input.attr("name")] = input.val().trim();  
          });
          data['contacts'].push(item);
        });
        _this.putData(_this, data, flag);
        $(this).addClass('disabled');
      });

    },
    render: function(){
      
    },
    refreshData: function(flag){
      var company_id = $('#mainCompanyDetailsDataContainer').attr('data-id');
      var url = ApiUrls.companies_list+'/'+company_id+'/company_info?flag=' + flag;
      $.ajax({
        url: url,
        method: 'GET',
        dataType: 'json',
        processData: false,
        cache: false,
        headers: { 'X-CSRFToken': $.cookie('apros_csrftoken')},
        success: function (data, status) 
        { 
          if (data['flag'] == 'invoicing')
          {
            var invoicingEditContainer = $('#companyInfoInvoicingDetailsEdit');
            invoicingEditContainer.hide();
            var invoicing = data['invoicing'];
            var invoicingContainer = $('#companyInfoInvoicingDetailsData');
            invoicingContainer.find('.fullNameText').text(invoicing['full_name']);
            invoicingContainer.find('.titleText').text(invoicing['title']);
            var addressText = '' + invoicing['address1'] + ', ' +  invoicing['address2']
            var cityStatePostalText = '' + invoicing['city'] + ', ' +  invoicing['state'] + ' ' + invoicing['postal_code']
            invoicingContainer.find('.addressText').text(addressText);
            invoicingContainer.find('.cityStatePostalText').text(cityStatePostalText);
            invoicingContainer.find('.countryText').text(invoicing['country']);
            invoicingContainer.find('.poText').text(invoicing['po']);
            invoicingContainer.find('.ipText').text(invoicing['identity_provider']);

            $.each(invoicing, function(key,value) {
              if (value == '-')
              {
                invoicing[key] = ''
              }
            });
            invoicingEditContainer.find('.fullNameInput').val(invoicing['full_name']);
            invoicingEditContainer.find('.titleInput').val(invoicing['title']);
            invoicingEditContainer.find('.address1Input').val(invoicing['address1']);
            invoicingEditContainer.find('.address2Input').val(invoicing['address2']);
            invoicingEditContainer.find('.cityInput').val(invoicing['city']);
            invoicingEditContainer.find('.stateInput').val(invoicing['state']);
            invoicingEditContainer.find('.postalCodeInput').val(invoicing['postal_code']);
            var selectableCountries = $.fn['countrySelect'].getCountryData();
            for (var i = 0; i<selectableCountries.length;i++)
            { 
              if (selectableCountries[i].name == invoicing['country'])
              {
                $('.countryText').text(invoicing['country']);
                $("#country_edit").countrySelect("selectCountry", selectableCountries[i].iso2);
              }  
            }
            invoicingEditContainer.find('.poInput').val(invoicing['po']);

            invoicingContainer.show();
            $('#companyInfoInvoicingDetails .companyInvoicingDetailsEditButton').show();
          }
          else if (data['flag'] == 'contacts')
          {
            var contactsWrapper = $('#companyInfoContacts');
            contactsWrapper.find('.companyInfoContactsEdit').hide();

            var contacts = data['contacts'];
            var contactsRows = contactsWrapper.find('.companyContactsRow');
            contactsRows.each(function (index, value){
              var _this = this;
              var contactType = $(_this).find('.contactTypeText');
              for(i=0;i<contacts.length;i++)
              {
                if(contactType.text() == contacts[i]['type'])
                {
                  contactType.text(contacts[i]['type']);
                  $(_this).find('.fullNameText').text(contacts[i]['full_name']);
                  $(_this).find('.titleText').text(contacts[i]['title']);
                  $(_this).find('.emailText').text(contacts[i]['email']);
                  $(_this).find('.phoneText').text(contacts[i]['phone']);
                  $.each(contacts[i], function(key,value) {
                    if (value == '-')
                    {
                      contacts[i][key] = ''
                    }
                  });
                  $(_this).find('.fullNameInput').val(contacts[i]['full_name']);
                  $(_this).find('.titleInput').val(contacts[i]['title']);
                  $(_this).find('.emailInput').val(contacts[i]['email']);
                  $(_this).find('.phoneInput').val(contacts[i]['phone']);
                }
              } 
            });

            contactsWrapper.find('.companyInfoContactsData').show();
            contactsWrapper.find('.companyContactsEditButton').show();
          }
          else 
          {
            console.log("Ajax failed to fetch data");
          }
        },
        error: function(data, status)
        {
          console.log("Ajax failed to fetch data");
        }
      });
    },
    putData: function(_this, data, flag){
      var company_id = $('#mainCompanyDetailsDataContainer').attr('data-id');
      var url = ApiUrls.companies_list+'/'+company_id+'/company_info?flag=' + flag;
      $.ajax({
        url: url,
        method: 'PUT',
        dataType: 'json',
        data: JSON.stringify(data),
        processData: false,
        cache: false,
        headers: { 'X-CSRFToken': $.cookie('apros_csrftoken')},
        success: function (data, status) 
        {
          if(data['errors']){
            var errors = '';
            var error_count = 0;
            for(var i in data['errors']){
              errors +=  '\n' + data['errors'][i];
              error_count += 1;
            }
            var error_template = ngettext(
                'Please correct following error: %(errors)s',
                'Please correct following errors: %(errors)s',
                error_count
            );

            alert(interpolate(error_template, {'errors': errors}, true));
            return;
          }
          if (data['flag'] == 'invoicing')
          {
            _this.refreshData(flag);
          }
          else if (data['flag'] == 'contacts')
          {
            _this.refreshData(flag);
          }
          else 
          {
            console.log("Ajax failed to fetch data");
          }
        },
        error: function(data, status)
        {
          console.log("Ajax failed to fetch data");
        }
      });
    }
  });
