  Apros.collections.AdminCourses = Backbone.PageableCollection.extend({
    model: Apros.models.AdminCourse,
    url: ApiUrls.courses_list,
    mode: "client",
    state: {
      firstPage: 1,
      pageSize: 50
    },
    queryParams: {
      currentPage: 0,
      totalPages: null,
      totalRecords: null,
      page_size: 0,
    }
  });