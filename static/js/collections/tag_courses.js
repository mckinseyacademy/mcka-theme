  Apros.collections.TagCourses = Backbone.Collection.extend({
    initialize: function(options){
      this.url = options.url;
    },
    model: Apros.models.AdminCourse,
    parse: function(data){
      tag_courses = data['courses'];
      this.tagDetails = data['name'];
      return tag_courses;
    }
  });