''' check Learner Dashboard existence for user/course/client '''
from django.conf import settings
from courses.models import FeatureFlags
from courses.user_courses import get_current_course_for_user
from api_client import user_api
from accounts.controller import set_learner_dashboard_in_session

class LearnerDashboardCheck(object):

    def process_request(self, request):

        if request.user.is_authenticated() and settings.LEARNER_DASHBOARD_ENABLED:
            if 'course_id' not in request.session:
                set_learner_dashboard_in_session(request)
