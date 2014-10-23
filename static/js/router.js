var Router = Backbone.Router.extend({
  routes: {
    '':                                       'home',
    'contact/':                               'contact',
    'courses/*course_id/progress':            'course_progress',
    'courses/*course_id/progress/*user_id':   'course_progress',
    'courses/*course_id/overview':            'course_overview',
    'courses/*course_id/cohort':              'course_cohort',
    'courses/*course_id/group_work':          'course_group_work',
    'courses/*course_id/resources':           'course_resources',
    'courses/*course_id/lessons/*lesson_id':  'course_lesson',
    'courses/*course_id':                     'course_index',
    'admin/client-admin/*organization_id/courses/*course_id/analytics':   'client_admin_course_analytics',
    'admin/client-admin/*organization_id/courses/*course_id':  'client_admin_course_info'
  },

  home: function() {
    var el = $('#home-landing');
    new Apros.views.HomeLanding({el: el}).render();
  },

  contact: function() {
    var el = $('#contact-page');
    new Apros.views.Contact({el: el}).render();
    $('#support_success').foundation('reveal', 'open');
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
    if (container.length && typeof OO !== 'undefined') {
      OO.Player.create('mk-player', container.data('video-id'), {width: '100%', height: '100%'});
    }
  },

  course_cohort: function(course_id) {
    new Apros.views.CourseCohort({el: $('#course-cohort')}).render();
  },

  course_group_work: function(course_id) {
  },

  course_resources: function(course_id) {
  },

  course_discussion: function(course_id) {
  },

  client_admin_course_analytics: function(organization_id, course_id) {
    var participantsModel = new Apros.models.ParticipantsAnalyticsChart();
    new Apros.views.AdminAnalyticsParticipantActivity({model: participantsModel,
                                                      el: $('#admin-analytics-participant-activity'),
                                                      client_id: organization_id,
                                                      course_id: course_id});
    var progressModel = new Apros.models.AnalyticsProgressChart();
    new Apros.views.AdminAnalyticsProgress({model: progressModel,
                                          el: $('#admin-analytics-progress'),
                                          client_id: organization_id,
                                          course_id: course_id});
  },

  client_admin_course_info: function(organization_id, course_id) {
    var model = new Apros.models.CourseInfoStatusChart();
    new Apros.views.ClientAdminCourseInfo({model: model,
                                          el: $('#course-status-chart'),
                                          client_id: organization_id,
                                          course_id: course_id});
  },

  course_lesson: function(courseId, lessonId) {
    var el = $('#course-lessons'),
        collection = new Apros.collections.CourseNotes(null, {courseId: courseId})
    new Apros.views.CourseLesson({el: el, collection: collection}).render();

  }
});

Apros.Router = new Router;
