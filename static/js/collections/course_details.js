Apros.collections.CourseDetails = Backbone.PageableCollection.extend({
  path:'',
  initialize: function (models, options) {
        this.path = options.path;
        this.url = ApiUrls.courses_list + '/' + this.path;
    },
  model: Apros.models.Course_Details,
  mode: "infinite",
  state: {
    firstPage:1,
    pageSize: 50
  },
  queryParams: {
    currentPage: "page",
    totalPages: null,
    totalRecords: null,
    include_slow_fields: false,
    ids: false,
    page_size: 50,
  },
  parseLinks: function (resp, options) {
    returnObject = {};
    num_of_pages = Math.ceil(resp.full_length/this.state.pageSize)
    current_page = resp.current_page
    if (parseInt(current_page) < parseInt(num_of_pages)){
      queryParameters = this.state.currentPage + '=' + (parseInt(current_page++)) ;
      returnObject['next'] = this.url + '?' + queryParameters;
    }
    return returnObject;
  },
  parse: function(data) {
    participants = data.results;
    return participants;
  },
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
    backup_page = this.state['currentPage'];
    this.state['currentPage'] = 1;
    this.fetch({update: true, remove:false, success:function(collection, response, options){
      data = response.results;
      for (var user in data)
      {
        userData = data[user];
        modelData = collection.fullCollection.models.filter(function(el){return el.attributes.id == userData.id})
        if (modelData.length > 0)
          modelData[0].set({progress: userData.progress});
      }
      collection.slowFieldsSuccess(collection, response, options)
    }});
    this.state['currentPage'] = backup_page;
    this.queryParams['include_slow_fields'] = false;
  },
  saveCurrentPageSlowState: function(idFieldName, slowAttributeName){
    listOfIds = [];
    _this = this;
    this.fullCollection.each(function(model){       
        if (model.get(_this.slowFieldsCollectionFieldIdentifier) == '.'){
          listOfIds.push(model.get(_this.slowFieldsFetchIdentifier));
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
          collection.saveCurrentPageSlowState();
          collection.fetchSlowFields(collection.slowFieldsFetchCount);
      }
    },
  getSlowFetchedStatus: false,
  pageAndIdConnector: [],
  slowFieldsFetchCount: 5,
  slowFieldsFetchIdentifier:'id',
  slowFieldsCollectionFieldIdentifier:'progress',
});