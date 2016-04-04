var ApiUrls = {
  courses_list: '/admin/api/courses',
  participants_list: '/admin/api/participants',
  validate_participant_email: '/admin/api/participants/validate_participant_email',
  validate_participant_username: '/admin/api/participants/validate_participant_username',
  participant_organization_get_api: function(user_id)
  {
  	return this.participants_list+'/'+user_id+'/organizations';
  },
  course_details: '/admin/api/courses'
}