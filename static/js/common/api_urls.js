var ApiUrls = {
  courses_list: '/admin/api/courses',
  manager_dashboard: '/admin/manager/courses',
  participants_list: '/admin/api/participants',
  companies_list: '/admin/api/companies',
  cache: '/admin/api/cache',
  participant_manage_courses: function(user_id, course_id)
  {
    return this.participants_list+'/'+user_id+'/course_manage/'+ course_id;
  },
  participant_organization_get_api: function()
  {
  	return this.participants_list+'/organizations';
  },
  participant_courses_get_api: function()
  {
    return this.participants_list+'/courses';
  },
  company_admin_get_post_put_delete: function(user_id)
  {
    return this.participants_list+'/'+user_id+'/admin_companies';
  },
  cached_resource_api: function(resource_name)
  {
    return this.cache+'/'+resource_name;
  },
  file_upload:"/admin/api/s3file",
  validate_participant_email: '/admin/api/participants/validate_participant_email',
  validate_participant_username: '/admin/api/participants/validate_participant_username',
  course_details: '/admin/api/courses',
  email_templates: '/admin/api/email-templates',
  email: '/admin/api/email',
  company: '/admin/api/companies/',
  tags: '/admin/api/tags',
  admin_bulk_task: '/admin/api/admin_bulk_task/',
  mobileapps: '/admin/api/mobileapps'
}
