  Apros.collections.AdminCourses = Backbone.PageableCollection.extend({
    model: Apros.models.AdminCourse,
    url: ApiUrls.courses_list,
    mode: "infinite",
    state: {
      firstPage: 1,
      pageSize: 100
    },
    queryParams: {
      currentPage: "page",
      totalPages: null,
      totalRecords: null,
      page_size: 100,
    },
    parseLinks: function (resp, options){
      returnObject={};
      if (resp['next'] != null){
        returnObject['next'] = ApiUrls.courses_list + '?'+resp['next'].split('?')[1];
      }
      if (resp['previous'] != null){
        returnObject['prev'] = ApiUrls.courses_list + '?'+resp['previous'].split('?')[1];
      }
      return returnObject;
    },
    parse: function(data){
      courses = data.results;
      return courses;
    }
  });