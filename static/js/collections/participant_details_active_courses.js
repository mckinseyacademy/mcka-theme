Apros.collections.ParticipantDetailsActiveCourses = Backbone.Collection.extend({
  initialize: function(options){
    this.url = options.url;
  },
  model: Apros.models.AdminCourse,
  fetchSlowFields: function(fetchNumber){
    this.getSlowFetchedStatus = false;
    this.queryParams['include_slow_fields'] = true;
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
        this.queryParams['include_slow_fields'] = false;
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
    this.fetchExtended({update:true,remove:false, success:function(collection, response, options){
      data = response;
      for (var user in data)
      {
        userData = data[user];
        for (var model in collection.models)
        {
          modelData = collection.models[model]
          if (modelData.attributes.id == userData.id)
          {
            modelData.set({progress: userData.progress})
            modelData.set({proficiency: userData.proficiency})
            break;
          }
        } 
      }
      collection.slowFieldsSuccess(collection, response, options)
    }});
    this.queryParams['include_slow_fields'] = false;
  },
  saveCurrentPageSlowState: function(idFieldName, slowAttributeName){
    listOfIds = [];
    this.each(function(model){       
        if (model.get(slowAttributeName) == '.'){
          listOfIds.push(model.get(idFieldName));
        }
      });
    this.pageAndIdConnector = listOfIds;
  },
  slowFieldsSuccess: function(collection, response, options){
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
        collection.saveCurrentPageSlowState(collection.slowFieldsFetchIdentifier,collection.slowFieldsCollectionFieldIdentifier);
        collection.fetchSlowFields(collection.slowFieldsFetchCount);
    }
  },
  fetchExtended: function(options) {
    if (typeof options == 'undefined')
      options = {}
    options['data'] = $.param(this.queryParams);
    this.fetch(options);
  },
  queryParams: {
    include_slow_fields: false,
    ids: false
  },
  getSlowFetchedStatus: false,
  pageAndIdConnector: [],
  slowFieldsFetchCount: 5,
  slowFieldsFetchIdentifier:'id',
  slowFieldsCollectionFieldIdentifier:'progress'
});