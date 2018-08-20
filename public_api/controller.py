''' Core logic to sanitise information for views '''
from django.http import Http404

from courses.models import FeatureFlags


def add_course_feature_flag_in_list(feature_flag, course_id):
    """
    append feature flag of required course in list
    """
    try:
        feature_flags = FeatureFlags.objects.get(course_id=course_id)
        feature_flag.append({feature_flags.course_id: feature_flags.as_json()})
    except:
        raise Http404()

