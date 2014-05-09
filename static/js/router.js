var Router = Backbone.Router.extend({
  routes: {
    'courses/*course_id/view/progress': 'course_progress'
  },

  course_progress: function(course_id) {
    var model = new Apros.models.Course({id: course_id});
    new Apros.views.CourseProgress({model: model, el: $('#course_progress')}).render()
  }
});

Apros.Router = new Router;
