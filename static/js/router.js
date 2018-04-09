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
    'admin/client-admin/*organization_id/courses/*course_id/download_course_report':  '',
    'admin/client-admin/*organization_id/courses/*course_id/branding':  '',
    'admin/client-admin/*organization_id/courses/*course_id/branding/create_edit':  '',
    'admin/client-admin/*organization_id/courses/*course_id/learner_dashboard':  '',
    'admin/client-admin/*organization_id/courses/*course_id/learner_dashboard/discover/list':  '',
    'admin/client-admin/*organization_id/courses/*course_id/learner_dashboard/milestone/list':  '',
    'admin/client-admin/*organization_id/courses/*course_id':  'client_admin_course_info',
    'admin/course-meta-content/items/*course_id': 'admin_course_meta',
    'admin/course-meta-content':'course_meta_content',
    'admin/participants': 'participants_list',
    'admin/participants/*id': 'initialize_participant_details',
    'admin/courses/': 'admin_courses',
    'admin/courses/*course_id/': 'admin_course_details_participants',
    'admin/clients/*client_id/courses_without_programs': 'assign_students_in_courses',
    'admin/clients/*client_id/mass_student_enroll': 'mass_student_enroll',
    'admin/clients/*client_id': 'client_details_view',
    'admin/companies': 'companies_list',
    'admin/companies/*company_id/linkedapps/*app_id': 'company_mobileapp_details',
    'admin/companies/*company_id/courses/*course_id': 'admin_course_details_participants',
    'admin/companies/*company_id/participants/*id': 'initialize_participant_details',
    'admin/companies/*company_id/learner_dashboards': 'company_learner_dashboards',
    'admin/companies/*company_id': 'company_details_courses',
    'admin/workgroup':'workgroup_main',
    'admin/programs/*program_id/courses': 'program_courses_main',
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
      OO.ready(function() {
        OO.Player.create(
          'mk-productwalkthrough-video',
           container.data('video-id')
        );
      });
    }
  },

  course_index: function(course_id) {
    if (typeof scorm_data == "undefined")
      scorm_data = {}
    scorm_data.courseId = course_id;
    var el = $('#home-courses');
    new Apros.views.HomeCourses({el: el}).render();
    COURSE_MAIN_PAGE = true;
    if (SCORM_SHELL)
    {
      SendGradebookToScormShell();
      SendProgressToScormShell();
      SendCompletionToScormShell();
      SendFullGradebookToScormShell();
    }
  },

  course_progress: function(course_id) {
    var model = new Apros.models.Course({id: course_id});
    new Apros.views.CourseProgress({model: model, el: $('#course-progress')}).render()
  },

  course_overview: function(course_id) {
    var container = $('#mk-player');
    if (container.length && typeof OO !== 'undefined') {
      OO.ready(function() {
        OO.Player.create('mk-player', container.data('video-id'));
      });
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

    if (typeof scorm_data == "undefined")
      scorm_data = {}
    scorm_data.courseId = courseId;
    scorm_data.lessonId = lessonId;
    scorm_data.moduleId = moduleId;

    var el = $('#course-lessons'),
        collection = new Apros.collections.CourseNotes(null, {courseId: courseId})
    new Apros.views.CourseLesson({el: el, collection: collection}).render();

  },

  admin_course_meta: function(courseId) {
    var el = $('#feature-flags');
    new Apros.views.AdminCourseMeta({el: el}).render();
  },

  companies_list: function(){
    var collection = new Apros.collections.Companies();
    var companies_list_view = new Apros.views.CompaniesListView({collection: collection, el: '#companiesListViewGridBlock'});
    companies_list_view.render();
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
    var companyPageFlag = $('#courseDetailsDataWrapper').attr('company-page');
    $('#courseDetailsMainContainer').find('.courseDetailsTopic').each(function(index, value){
      val = $(value);
      val.show();
    });
    $('#coursesDownloadStatsButton').show();
    var courseId = $('#courseDetailsDataWrapper').attr('data-id');
    ApiUrls.course_details_stats = ApiUrls.course_details+'/'+courseId+'/stats/';
    ApiUrls.course_details_engagement = ApiUrls.course_details+'/'+courseId+'/engagement/';
    if (companyPageFlag == 'True')
    {
      var companyId = $('#courseDetailsDataWrapper').attr('company-id');
      ApiUrls.course_details_stats = ApiUrls.course_details_stats + '?company_id=' + companyId;
      ApiUrls.course_details_engagement = ApiUrls.course_details_engagement + '?company_id=' + companyId;
    }
    var courseDetailsEngagement = new Apros.collections.CourseDetailsEngagement({url: ApiUrls.course_details_engagement});
    var course_details_engagement_view = new Apros.views.CourseDetailsEngagementView({collection: courseDetailsEngagement, el: '#courseDetailsEngagementViewGrid'});
    course_details_engagement_view.render();

    var discussion_feature = $('#discussionFeature').attr('value');
    if (discussion_feature == 'True')
    {
      var courseDetailsStats = new Apros.collections.CourseDetailsStats({url: ApiUrls.course_details_stats});
      var course_details_stats_view = new Apros.views.CourseDetailsStatsView({collection: courseDetailsStats, el: '#courseDetailsStatsViewGrid'});
      course_details_stats_view.render();

    }
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
  company_mobileapp_details: function(){
    var company_mobileapp_view = new Apros.views.CompanyMobileappDetails();
    company_mobileapp_view.render();

  },
  company_details_courses: function(company_id){
    $('#companyDetailsDataWrapper').find('.contentNavigationContainer').each(function(index, value){
      val = $(value);
      if (val.hasClass('companyCourses'))
        val.show();
      else
        val.hide();
    });
    var companyId = $('#mainCompanyDetailsDataContainer').attr('data-id');
    Apros.Router.linked_views['companyCourses']['drawn'] = true;
    var url = ApiUrls.companies_list+'/'+companyId+'/courses';
    var companyCourses = new Apros.collections.CompanyDetailsCourses({ url : url});
    var company_courses_view = new Apros.views.CompanyDetailsCoursesView({collection: companyCourses, el: '#companyDetailsCoursesViewGridBlock'});
    company_courses_view.render();
  },
  company_details_linked_apps: function(company_id){
    $('#companyDetailsDataWrapper').find('.contentNavigationContainer').each(function(index, value){
      val = $(value);
      if (val.hasClass('companyLinkedApps'))
        val.show();
      else
        val.hide();
    });
    var companyId = $('#mainCompanyDetailsDataContainer').attr('data-id');
    Apros.Router.linked_views['companyLinkedApps']['drawn'] = true;
    var url = ApiUrls.companies_list+'/'+companyId+'/linkedapps';
    var companyLinkedApps = new Apros.collections.CompanyLinkedApps({ url : url});

    var company_linked_apps_view = new Apros.views.CompanyLinkedAppsView({collection: companyLinkedApps, el: '#companyLinkedAppsViewGridBlock'});
    company_linked_apps_view.render();
  },

  company_learner_dashboards: function(company_id){
    $('#companyDetailsDataWrapper').find('.contentNavigationContainer').each(function(index, value){
      val = $(value);
      if (val.hasClass('companyLearnerDashboards'))
        val.show();
      else
        val.hide();
    });
    var companyId = $('#mainCompanyDetailsDataContainer').attr('data-id');
    Apros.Router.linked_views['companyLearnerDashboards']['drawn'] = true;
    var url = ApiUrls.companies_list+'/'+companyId+'/learner_dashboards';

    var companyLearnerDashboards = new Apros.collections.CompanyLearnerDashboards({ url : url});
    var company_learner_dashboards_view = new Apros.views.CompanyLearnerDashboardsView({
      collection: companyLearnerDashboards, el: '#companyLearnerDashboardsViewGridBlock'
    });

    company_learner_dashboards_view.render();
  },
  assign_students_in_courses: function(client_id)
  {
    if ($(".course-box").length === 0)
    {
      $(document).on("nice_checkbox_generated", function(event, parentContainer)
      {
        AdjustCompanyParticiantsNumber(client_id, parentContainer, {"force_refresh":true});
      });
      CreateNiceAjaxTemplate(".coursesCheckboxContainer", 'courses_list', {"template":$("#courseCheckboxTemplate").html(), "type":"checkbox"}, {"force_refresh":true});
    }
  },
  mass_student_enroll: function(client_id){
    massParticipantsInit();
  }, 
  workgroup_main: function(){
    if($(".select-group-wrapper").attr('data-enable-cache')==='true')
    {
      CreateNiceAjaxSelect('.select-group-wrapper', 'courses_list', {'name':'select-course','id':''}, {"value":'select', "name": '- Select -'}, {"force_refresh":true});
    }
  },
  client_details_view: function()
  {
    $(document).on("csv_chunk_sent", CSVDataCollector);
    $('.manage-student-list .downloadStudentList').on("click", function()
    {
      GenerateCSVDownloader(this);
    });
  },
  course_meta_content: function()
  {
    var container = "#course_meta_content_main_container";
    if ($(container).length)
      if($(container).attr('data-enable-cache')==='true')
        CreateNiceAjaxLinkList(container, 'courses_list', '/admin/course-meta-content/items/', {"force_refresh":true});
  },
  program_courses_main: function(program_id)
  {
    var container = '#course-list table';
    if ($(container).length)
    {
      CreateNiceAjaxTable(container, 'courses_list', {"header_fields":['Name', 'Instance'],"table_classes":"course-list", "table_ids":"course-list-table", "row_classes":"course"},
        {"force_refresh":true, "program_id":program_id, "data_format":"table"});
      $(document).on("nice_table_generated", function(event, container_name){
        if (container_name != '#course-list table')
          return;
        var selection = {
        selector: '.course-list .course',
        submit_name: 'courses',
        minimum_count: 0,
        minimum_count_message: gettext("Please select at least one course")
        };

        var activator = {
          selector: '#course-program-action'
        }
        enable_selection(selection, activator);

        $('.student-list').dataTable({
            paging: false,
            autoWidth: false,
            scrollX: true,
            "dom": '<"top small-6"f>rt<"bottom"ilp><"clear">'
        });
      });
    }
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
  },
  'companyCourses': {
    'function':Apros.Router.company_details_courses,
    'drawn': false
  },
  'companyLearnerDashboards': {
    'function':Apros.Router.company_learner_dashboards,
    'drawn': false
  },
  'companyLinkedApps': {
    'function':Apros.Router.company_details_linked_apps,
    'drawn': false
  },
}

Apros.Router.HashPageChanger = function(element) {
  var el = $(element);
  var _selectedClass = el.attr('data-target');
  var _parentContainer = $(el.attr('data-container'));
  el.parent().parent().find('.hashPageButton').css('font-weight','');
  el.css('font-weight','bold');
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

