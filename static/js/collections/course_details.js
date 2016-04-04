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
    pageSize: 100
  },
  queryParams: {
    currentPage: "page",
    totalPages: null,
    totalRecords: null,
    include_slow_fields: false,
    ids: false,
    page_size: 100,
  },
  parseLinks: function (resp, options) {
    console.log()
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
      data = data.results;
      for (var userIndex = 0;userIndex < data.length;userIndex++)
      {
        userData = data[userIndex];
        modelData = collection.fullCollection.models.filter(function(el){return el.attributes.id == userData.id})
        if (modelData.length > 0)
          modelData[0].set({progress: userData.progress, assessments: userData.assessments, groupworks: userData.groupworks});
      }
      collection.slowFieldsSuccess(collection);
    })
    .fail(function(data) {
      console.log("Ajax failed to fetch data");
      console.log(data)
    })
  },
  getSlowFetchedStatus: false,
  pageAndIdConnector: [],
  slowFieldsFetchCount: 10,
  slowFieldsFetchIdentifier:'id',
  slowFieldsCollectionFieldIdentifier:'progress',
});