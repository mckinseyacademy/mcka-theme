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
    'admin/courses/*course_id/': 'admin_course_details_participants'
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
  initialize_participant_details: function()
  {
    var view = new Apros.views.ParticipantEditDetailsView();
    view.render();
  },
  participant_details_active_courses: function(){
    var url = ApiUrls.participants_list+'/'+$('#participantsDetailsDataWrapper').attr('data-id')+'/active_courses';
    var collection = new Apros.collections.ParticipantDetailsActiveCourses({url: url});
    var participant_details_active_courses_view = new Apros.views.ParticipantDetailsActiveCoursesView({collection: collection, el: '#participantDetailsActiveCoursesViewGrid'});
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

    $('#courseBulkActionsMainContainer').on('click','.bulkChangeStatus',function()
    {
      var selectedRowsIdsLen = courses_details_view.coursesListDetailsViewGrid.selectedRows.length;
      $('#courseDetailsMainModal').find('.courseModalTitle').text('Change Status');
      $('#courseDetailsMainModal').find('.courseModalStatus').text('Selected: '+selectedRowsIdsLen+', Successful: 0, Failed: 0');
      $('#courseDetailsMainModal').find('.courseModalDescription').text('Change status of all selected participants to:');
      $('#courseDetailsMainModal').find('.courseModalContent').html(
        '<input type="radio" name="status" value="Active" id="participantCheckbox"><label for="participantCheckbox">Active</label>'+
        '<input type="radio" name="status" value="Observer" id="observerCheckbox"><label for="observerCheckbox">Observer</label>'+
        '<input type="radio" name="status" value="TA" id="taCheckbox"><label for="taCheckbox">TA</label>'
      );
      if(courses_details_view.coursesListDetailsViewGrid.selectedRows.length === 0) {
        alert("You need to select at least one participant to be able to apply bulk actions.")
      }
      else {
        $('#courseDetailsMainModal').find('.courseModalControl').find('.saveChanges').off().on('click', function()
        {
          var selectedRowsIds = courses_details_view.coursesListDetailsViewGrid.selectedRows;
          var selectedVal = "";
          var selected = $("#courseDetailsMainModal input[type='radio']:checked");
          if (selected.length > 0) {
              selectedVal = selected.val();
          }
          else
          {
            alert('You need to select status!');
            return;
          }
          var dictionaryToSend = {type:'status_change', new_status: selectedVal, list_of_items:[]};
          for (selectedRowsIndex in selectedRowsIds)
          {
            var id = selectedRowsIds[selectedRowsIndex];
            var selectedModel = courseDetails.fullCollection.get(id);
            var item ={ id: id, existing_roles: selectedModel.attributes.user_status};
            dictionaryToSend.list_of_items.push(item);
          }
          var url = ApiUrls.course_details+'/'+courseId;
          var options = {
            url: url,
            data: JSON.stringify(dictionaryToSend),
            processData: false,
            type: "POST",
            dataType: "json"
          };

          options.headers = { 'X-CSRFToken': $.cookie('apros_csrftoken')};
          $.ajax(options)
          .done(function(data) {
            console.log(data);
            if (data['status'] == 'ok')
            {
              courses_details_view.realtimeStatus(url, '#courseDetailsMainModal .courseModalStatus', data['task_id']);
              var new_status = data['data'].new_status
              for (itemIndex in data['data'].list_of_items)
              {
                var itemData = data['data'].list_of_items[itemIndex]
                var selectedModel = courseDetails.fullCollection.get(itemData.id);
                selectedModel.set({})
              }
            }
            })
          .fail(function(data) {
            console.log("Ajax failed to fetch data");
            console.log(data);
            })
        });
        $('#courseDetailsMainModal').foundation('reveal', 'open');
      }
    }); 
  },
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
}

