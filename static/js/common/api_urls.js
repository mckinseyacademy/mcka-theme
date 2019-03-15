var ApiUrls = {
  courses_list: '/admin/api/courses',
  cohorts_root: '/admin/api/cohorts',
  cohort_handler: function(course_id, cohort_id) {
    return this.cohorts_root + '/courses/' + course_id + '/cohorts/' + cohort_id;
  },
  cohorts_list: function(course_id) {
    return this.cohorts_root + '/courses/' + course_id + '/cohorts/';
  },
  cohorts_settings: function(course_id) {
    return this.cohorts_root + '/courses/' + course_id + '/settings';
  },
  cohorts_users: function(course_id, cohort_id) {
    return this.cohorts_root + '/courses/' + course_id + '/cohorts/' + cohort_id + '/users';
  },
  manager_dashboard: '/admin/manager/courses',
  participants_list: '/admin/api/participants',
  companies_list: '/admin/api/companies',
  cache: '/admin/api/cache',
  participant_manage_courses: function(user_id, course_id) {
    return this.participants_list + '/' + user_id + '/course_manage/' + course_id;
  },
  participant_organization_get_api: function() {
    return this.participants_list + '/organizations';
  },
  participant_courses_get_api: function() {
    return this.participants_list + '/courses';
  },
  company_admin_get_post_put_delete: function(user_id) {
    return this.participants_list + '/' + user_id + '/admin_companies';
  },
  cached_resource_api: function(resource_name) {
    return this.cache + '/' + resource_name;
  },
  course_blocks: function(courseId) {
    return ApiUrls.course_details + '/' + (courseId || ApiUrls.currentCourseId) + '/blocks/';
  },
  course_reports: function(courseId) {
    return '/admin/api/problem_response_reports/course/' + (courseId || ApiUrls.currentCourseId) + '/';
  },
  file_upload: '/admin/api/s3file',
  validate_participant_email: '/admin/api/participants/validate_participant_email',
  validate_participant_username: '/admin/api/participants/validate_participant_username',
  course_details: '/admin/api/courses',
  email_templates: '/admin/api/email-templates',
  email: '/admin/api/email',
  company: '/admin/api/companies/',
  tags: '/admin/api/tags',
  admin_bulk_task: '/admin/api/admin_bulk_task/',
  mobileapps: '/admin/api/mobileapps',
  import_progress: '/admin/api/participants/import_progress'
};
