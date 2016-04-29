var ApiUrls = {
  courses_list: '/admin/api/courses',
  participants_list: '/admin/api/participants',
  companies_list: '/admin/api/companies',
  validate_participant_email: '/admin/api/participants/validate_participant_email',
  validate_participant_username: '/admin/api/participants/validate_participant_username',
  participant_organization_get_api: function()
  {
  	return this.participants_list+'/organizations';
  },
  participant_courses_get_api: function()
  {
    return this.participants_list+'/courses';
  },
  course_details: '/admin/api/courses',
  email_templates: '/admin/api/email-templates'
}