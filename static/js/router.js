var Router = Backbone.Router.extend({
  routes: {
    '': 'home',
    'courses/*course_id/view/progress': 'course_progress'
  },

  home: function() {
    el = $('#home-grid');
    if (el.length) {
      new Apros.views.HomeGrid({el: el}).render();
    }
  },

  course_progress: function(course_id) {
    var model = new Apros.models.Course({id: course_id});
    new Apros.views.CourseProgress({model: model, el: $('#course-progress')}).render()
  }
});

Apros.Router = new Router;
