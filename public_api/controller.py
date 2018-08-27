''' Core logic to sanitise information for views '''
from api_client import user_api
from courses.models import FeatureFlags


def get_course_feature_flag(user_id, feature_flag, course_id):
    """
    check the required course feature flag entry in database and then add in list
    """
    try:
        feature_flags = FeatureFlags.objects.get(course_id=course_id)
        feature_flag.append({feature_flags.course_id: feature_flags.as_json()})
    except FeatureFlags.DoesNotExist:
        feature_flags = None
    if not feature_flags:
        try:
            user_api.get_user_course_detail(user_id, course_id)
            create_and_add_course_feature_flag_in_list(feature_flag, course_id)
        except:
            return feature_flags

    return feature_flags


def create_and_add_course_feature_flag_in_list(feature_flag, course_id):
    """
    append feature flag of required course in list
    """
    feature_flags, created = FeatureFlags.objects.get_or_create(course_id=course_id)
    feature_flag.append({feature_flags.course_id: feature_flags.as_json()})

