  Apros.collections.Companies = Backbone.Collection.extend({
    model: Apros.models.Company,
    url: ApiUrls.companies_list,
    queryParams: {
      include_slow_fields: false,
    },
    parse: function(data){
      companies = data;
      return companies;
    },
    fetchSlowFields: function(fetchNumber){
    this.getSlowFetchedStatus = false;
    if (fetchNumber > 0)
    {
      listOfIds = [];
      if (this.pageAndIdConnector.length > 0)
      {
        dont_fetch = false;
        listOfIds = this.pageAndIdConnector;
      }
      if (listOfIds.length == 0)
      {
        this.queryParams['ids'] = false;
        return;
      }
      else
      {
        if (listOfIds.length < fetchNumber)
        {
          this.getSlowFetchedStatus = false;
          this.queryParams['ids'] = listOfIds.join();
        }
        else
        {
          this.getSlowFetchedStatus = true;
          this.queryParams['ids'] = listOfIds.slice(0,fetchNumber).join();
        }      
      }
    }
    this.fetchSlowFieldsAjax(this);
    },
    saveCurrentPageSlowState: function(){
      listOfIds = [];
      _this = this;
      this.each(function(model){       
          if (model.get(_this.slowFieldsCollectionFieldIdentifier) == '.'){
            listOfIds.push(model.get(_this.slowFieldsFetchIdentifier));
          }
        });
      this.pageAndIdConnector = listOfIds;
    },
    slowFieldsSuccess: function(collection){
      if (collection.getSlowFetchedStatus)
      {
          if (collection.pageAndIdConnector.length < collection.slowFieldsFetchCount)
          {
            collection.pageAndIdConnector = [];
          }
          else
          {
            collection.pageAndIdConnector = collection.pageAndIdConnector.slice(collection.slowFieldsFetchCount, collection.pageAndIdConnector.length);
          }  
          collection.saveCurrentPageSlowState();
          collection.fetchSlowFields(collection.slowFieldsFetchCount);
      }
    },
    fetchSlowFieldsAjax: function(collection)
    {
      var optionsData = {ids:this.queryParams['ids'], include_slow_fields:true};
      var options = {
          url: this.url,
          data: optionsData,
          type: "GET",
          dataType: "json"
        };

      options.headers = { 'X-CSRFToken': $.cookie('apros_csrftoken')};
      $.ajax(options)
      .done(function(data) {
        for (var userIndex = 0;userIndex < data.length;userIndex++)
        {
          userData = data[userIndex];
          modelData = collection.models.filter(function(el){return el.attributes.id == userData.id})
          if (modelData.length > 0)
            modelData[0].set({numberParticipants: userData.numberParticipants});
        }
        collection.slowFieldsSuccess(collection);
      })
      .fail(function(data) {
        console.log("Ajax failed to fetch data");
        console.log(data)
      });
    },
    getSlowFetchedStatus: false,
    pageAndIdConnector: [],
    slowFieldsFetchCount: 5,
    slowFieldsFetchIdentifier:'id',
    slowFieldsCollectionFieldIdentifier:'numberParticipants',
  });