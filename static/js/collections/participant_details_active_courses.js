Apros.collections.ParticipantDetailsActiveCourses = Backbone.Collection.extend({
  initialize: function(options){
    this.url = options.url;
  },
  model: Apros.models.AdminCourse,
  parse: function(data) {
    courses = data;
    console.log(courses);
    return courses;
  }
});