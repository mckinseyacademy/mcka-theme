Apros.collections.Participants = Backbone.PageableCollection.extend({
  model: Apros.models.Participant,
  url: ApiUrls.participants_list,
  mode: "infinite",
  state: {
    firstPage:1,
    pageSize: 100
  },
  queryParams: {
    currentPage: "page",
    totalPages: null,
    totalRecords: null,
    page_size: 100,
  },
  parseLinks: function (resp, options) {
    returnObject={};
    if (resp['next'] != null){
      returnObject['next'] = ApiUrls.participants_list + '?'+resp['next'].split('?')[1];
    }
    if (resp['previous'] != null){
      returnObject['prev'] = ApiUrls.participants_list + '?'+resp['previous'].split('?')[1];
    }
    return returnObject;
  },
  parse: function(data) {
    participants = data.results; 
    return participants;
  },
  updateQuerryParams: function(options){
    for (key in options) {
      if (options[key]){
        this.queryParams[key] = options[key];
      }
      else{
        delete this.queryParams[key];
      }
    }
    this.state['pageSize'] = 100;
    this.queryParams['page_size'] = 100;
    this.queryParams['match'] = 'partial';
  }
});