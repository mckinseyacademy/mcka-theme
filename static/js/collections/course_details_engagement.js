  Apros.collections.CourseDetailsEngagement = Backbone.Collection.extend({
    initialize: function(options){
      this.url = options.url;
    },
    model: Apros.models.AdminCourseDetails,
    parse: function(data){
      course_details_engagement = data;
      return course_details_engagement;
    }
  });
