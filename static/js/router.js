var Router = Backbone.Router.extend({
  routes: {
    '': 'home',
    'courses/*course_id/view/progress': 'course_progress'
  },

  home: function() {
    var landing = $('#home-landing'),
        courses = $('#home-courses');
    if (landing.length) return new Apros.views.HomeLanding({el: landing}).render();
    if (courses.length) new Apros.views.HomeCourses({el: courses}).render();
  },

  course_progress: function(course_id) {
    var model = new Apros.models.Course({id: course_id});
    new Apros.views.CourseProgress({model: model, el: $('#course-progress')}).render()
  }
});

Apros.Router = new Router;
