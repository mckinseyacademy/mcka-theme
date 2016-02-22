Apros.collections.Participants = Backbone.PageableCollection.extend({
  model: Apros.models.Participant,
  url: ApiUrls.participants_list,
  mode: "infinite",
  state: {
    firstPage:1,
    pageSize: 50
  },
  queryParams: {
    currentPage: "page",
    totalPages: null,
    totalRecords: null,
    has_organizations: true,
    page_size: 50,
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
  }
});