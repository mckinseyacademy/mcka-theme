var Router = Backbone.Router.extend({
  routes: {
    '':                              'home',
    'courses/*course_id/progress':   'course_progress',
    'courses/*course_id/overview':   'course_overview',
    'courses/*course_id/cohort':     'course_cohort',
    'courses/*course_id/group_work': 'course_group_work',
    'courses/*course_id/resources':  'course_resources',
    'courses/*course_id':            'course_index'
  },

  home: function() {
    var el = $('#home-landing');
    new Apros.views.HomeLanding({el: el}).render();
  },

  course_index: function() {
    var el = $('#home-courses');
    new Apros.views.HomeCourses({el: el}).render();
  },

  course_progress: function(course_id) {
    var model = new Apros.models.Course({id: course_id});
    new Apros.views.CourseProgress({model: model, el: $('#course-progress')}).render()
  },

  course_overview: function(course_id) {
    var container = $('#mk-player');
    if (container.length) {
      OO.Player.create('mk-player', container.data('video-id'), {width: '100%', height: '100%'});
    }
  },

  course_cohort: function(course_id) {
    var model = new Apros.models.LocationData({id: course_id});
    new Apros.views.CourseCohort({model: model, el: $('#course-cohort')})
  },

  course_group_work: function(course_id) {
  },

  course_resources: function(course_id) {
  },

  course_discussion: function(course_id) {
  }
});

Apros.Router = new Router;
