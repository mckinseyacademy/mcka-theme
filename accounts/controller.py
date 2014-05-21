from api_client import user_api

def get_current_course_for_user(request):
    course_id = request.session.get("current_course_id", None)

    if not course_id and request.user:
        # TODO: Replace with logic for finding "current" course
        # For now, we just return first course
        courses = user_api.get_user_courses(request.user.id)
        if len(courses) > 0:
            course_id = courses[0].id

    return course_id