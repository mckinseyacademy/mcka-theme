var Router = Backbone.Router.extend({
  routes: {
    'courses/*course_id': 'home',
    'courses/*course_id/view/progress':     'course_progress',
    'courses/*course_id/view/cohort':       'course_cohort',
    'courses/*course_id/view/group_work':   'course_group_work',
    'courses/*course_id/view/resources':    'course_resources'
  },

  home: function() {
    var landing = $('#home-landing'),
        courses = $('#home-courses');
    if (landing.length) return new Apros.views.HomeLanding({el: landing}).render();
    if (courses.length) new Apros.views.HomeCourses({el: courses}).render();
  },

  course_progress: function(course_id) {
    $('#beta_content').foundation('reveal', 'open');
    var model = new Apros.models.Course({id: course_id});
    new Apros.views.CourseProgress({model: model, el: $('#course-progress')}).render()
  },

  course_cohort: function(course_id) {
    $('#beta_content').foundation('reveal', 'open');
    var model = new Apros.models.Course({id: course_id});
    new Apros.views.CourseCohort({model: model, el: $('#course-cohort')}).render()
  },

  course_group_work: function(course_id) {
    $('#beta_content').foundation('reveal', 'open');
  },

  course_resources: function(course_id) {
    $('#beta_content').foundation('reveal', 'open');
  }
});

Apros.Router = new Router;
