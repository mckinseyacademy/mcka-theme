var Router = Backbone.Router.extend({
  routes: {
    '':                                       'home',
    'home':                                   'protected_home',
    'contact/':                               'contact',
    'edxoffer/':                              'edxoffer',
    'productwalkthrough/':                    'productwalkthrough',
    'courses/*course_id/progress':            'course_progress',
    'courses/*course_id/progress/*user_id':   'course_progress',
    'courses/*course_id/overview':            'course_overview',
    'courses/*course_id/cohort':              'course_cohort',
    'courses/*course_id/group_work':          'course_group_work',
    'courses/*course_id/resources':           'course_resources',
    'courses/*course_id/lessons/*lesson_id/module/*module_id':  'course_lesson',
    'courses/*course_id':                     'course_index',
    'admin/client-admin/*organization_id/courses/*course_id/analytics':   'client_admin_course_analytics',
    'admin/client-admin/*organization_id/courses/*course_id/participants':  '',
    'admin/client-admin/*organization_id/courses/*course_id':  'client_admin_course_info',
    'admin/course-meta-content/items/*course_id': 'admin_course_meta',
    'admin/participants': 'participants_list',
    'admin/participants/*id': 'initialize_participant_details',
    'admin/courses/': 'admin_courses',
    'admin/courses/*course_id/': 'admin_course_details_participants',
    'admin/clients/*client_id/mass_student_enroll': 'mass_student_enroll'
  },

  home: function() {
    var el = $('#home-landing');
    new Apros.views.HomeLanding({el: el}).render();
  },

  protected_home: function() {
    this.home();
  },

  contact: function() {
    var el = $('#contact-page');
    new Apros.views.Contact({el: el}).render();
    $('#support_success').foundation('reveal', 'open');
  },

  edxoffer: function() {
    var el = $('#edxoffer-page');
    new Apros.views.Edxoffer({el: el}).render();
  },

  productwalkthrough: function() {
    var container = $('#mk-productwalkthrough-video');
    if (container.length && typeof OO !== 'undefined') {
      OO.Player.create('mk-productwalkthrough-video', container.data('video-id'), {width: '100%', height: '400px'});
    }
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

  course_lesson: function(courseId, lessonId, moduleId) {
    var el = $('#course-lessons'),
        collection = new Apros.collections.CourseNotes(null, {courseId: courseId})
    new Apros.views.CourseLesson({el: el, collection: collection}).render();

  },

  admin_course_meta: function(courseId) {
    var el = $('#feature-flags');
    new Apros.views.AdminCourseMeta({el: el}).render();
  },

  participants_list: function(){
    var collection = new Apros.collections.Participants();
    var participant_list_view = new Apros.views.ParticipantsInfo({collection: collection, el: '#participantsListViewGridBlock'});
    participant_list_view.render();
  },
  initialize_participant_details: function(user_id)
  {
    var view = new Apros.views.ParticipantEditDetailsView({url:  ApiUrls.participant_organization_get_api()});
    view.render();
  },
  participant_details_active_courses: function(){
    var user_id = $('#participantsDetailsDataWrapper').attr('data-id');
    var url = ApiUrls.participants_list+'/'+user_id+'/active_courses';
    var collection = new Apros.collections.ParticipantDetailsActiveCourses({url: url});
    var participant_details_active_courses_view = new Apros.views.ParticipantDetailsActiveCoursesView({collection: collection, el: '#participantDetailsActiveCoursesViewGrid', user_id: user_id});
    participant_details_active_courses_view.render();
  },

  participant_details_course_history: function(){
    var url = ApiUrls.participants_list+'/'+$('#participantsDetailsDataWrapper').attr('data-id')+'/course_history';
    var collection = new Apros.collections.ParticipantDetailsCourseHistory({url: url});
    var participant_details_course_history_view = new Apros.views.ParticipantDetailsCourseHistoryView({collection: collection, el: '#participantDetailsCourseHistoryViewGrid'});
    participant_details_course_history_view.render();
  },

  admin_courses: function(){
    var courses = new Apros.collections.AdminCourses();
    var courses_list_view = new Apros.views.CoursesListView({collection: courses, el: '#coursesListViewGridBlock'});
    courses_list_view.render();
  },

  admin_course_details_stats: function(course_id){
    $('#courseDetailsMainContainer').find('.courseDetailsTopic').each(function(index, value){
      val = $(value);
      val.show();
    });
    $('#coursesDownloadStatsButton').show();
    var courseId = $('#courseDetailsDataWrapper').attr('data-id');
    ApiUrls.course_details_stats = ApiUrls.course_details+'/'+courseId+'/stats/';
    ApiUrls.course_details_engagement = ApiUrls.course_details+'/'+courseId+'/engagement/';
    var courseDetailsEngagement = new Apros.collections.CourseDetailsEngagement({url: ApiUrls.course_details_engagement});
    var course_details_engagement_view = new Apros.views.CourseDetailsEngagementView({collection: courseDetailsEngagement, el: '#courseDetailsEngagementViewGrid'});
    var courseDetailsStats = new Apros.collections.CourseDetailsStats({url: ApiUrls.course_details_stats});
    var course_details_stats_view = new Apros.views.CourseDetailsStatsView({collection: courseDetailsStats, el: '#courseDetailsStatsViewGrid'});
    course_details_engagement_view.render();
    course_details_stats_view.render();

    var progressModel = new Apros.models.CourseDetailsTimelineChart();
    new Apros.views.AdminCourseDetailsTimeline({model: progressModel,
                                          el: $('#course-details-timeline'),
                                          course_id: courseId});
  },
  admin_course_details_participants: function(course_id){
    $('#courseDetailsMainContainer').find('.contentNavigationContainer').each(function(index, value){
      val = $(value);
      if (val.hasClass('courseParticipants'))
        val.show();
      else
        val.hide();
    });
    Apros.Router.linked_views['courseParticipants']['drawn'] = true;
    var courseId = $('#courseDetailsDataWrapper').attr('data-id');
    var courseDetails = new Apros.collections.CourseDetails([],{ path : courseId});
    var courses_details_view = new Apros.views.CourseDetailsView({collection: courseDetails, el: '#courseDetailsParticipantsGrid'});
    courses_details_view.render();
    var bulkActions = new Apros.views.CourseDetailsBulkActions({'courseId':courseId,'courses_details_view':courses_details_view, 'courseDetails':courseDetails});
    bulkActions.render(); 
  },
  mass_student_enroll: function(client_id){
    massParticipantsInit();
  }
});
Apros.Router = new Router;
Apros.Router.linked_views = {
  'courseParticipants': {
    'function':Apros.Router.admin_course_details_participants,
    'drawn': false
  },
  'courseStats': {
    'function':Apros.Router.admin_course_details_stats,
    'drawn': false
  },
  'participantDetailsContent': {
    'function': function(){},
    'drawn': false
  },
  'participantDetailsActiveCourses': {
    'function':Apros.Router.participant_details_active_courses,
    'drawn': false
  },
  'participantDetailsCourseHistory': {
    'function':Apros.Router.participant_details_course_history,
    'drawn': false
  }
}

Apros.Router.HashPageChanger = function(element) {
  _selectedClass = $(element).attr('data-target');
  _parentContainer = $($(element).attr('data-container'));
  _parentContainer.find('.contentNavigationContainer').each(function(index, value){
  val = $(value);
  if (val.hasClass(_selectedClass))
  {
    val.show();
    if (!Apros.Router.linked_views[_selectedClass]['drawn'])
    {
      Apros.Router.linked_views[_selectedClass]['drawn'] = true;
      Apros.Router.linked_views[_selectedClass]['function']();
    }
  }
  else
    val.hide();
  });
  updateHeader();
}

