  Apros.collections.ParticipantDetailsCourseHistory = Backbone.Collection.extend({
    initialize: function(options){
      this.url = options.url;
    },
    model: Apros.models.AdminCourse,
    parse: function(data){
      course_history = data;
      return course_history;
    }
  });