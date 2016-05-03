  Apros.collections.CompanyDetailsCourses = Backbone.Collection.extend({
    initialize: function(options){
      this.url = options.url;
    },
    model: Apros.models.CompanyDetailsCourses,
    parse: function(data){
      company_courses = data;
      return company_courses;
    }
  });