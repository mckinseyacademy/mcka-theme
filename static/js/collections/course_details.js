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
    page_size: 100,
    additional_fields: 'grades,roles,organizations,progress',
  },
  parseLinks: function (resp, options) {
    returnObject={};
    if (resp['next'] != null){
      returnObject['next'] = this.url + '?'+resp['next'].split('?')[1];
    }
    if (resp['previous'] != null){
      returnObject['prev'] = this.url + '?'+resp['previous'].split('?')[1];
    }
    return returnObject;
  },
  parse: function(data) {
    participants = data.results;
    return participants;
  },
  updateCompanyQuerryParams: function(company_id){
    this.queryParams['organizations'] = company_id;
  },
  updateCountQuerryParams: function(count){
    this.queryParams['count'] = count;
  }
});