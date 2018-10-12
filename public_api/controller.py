''' Core logic to sanitise information for views '''
from api_client import user_api
from courses.models import FeatureFlags, CourseMetaData


def get_course_ff_and_custom_taxonomy(user_id, course_ff_custom_taxonomy, course_id):
    """
    check the required course feature flag and custom taxonomy entry in database and then add in list
    """
    try:
        feature_flags = FeatureFlags.objects.get(course_id=course_id)
        course_meta_data = CourseMetaData.objects.get(course_id=course_id)
        course_ff_custom_taxonomy.append({feature_flags.course_id: {"feature_flags":feature_flags.as_json(),"custom_taxonomy":course_meta_data.as_json()}})
    except FeatureFlags.DoesNotExist:
        feature_flags = None
    if not feature_flags:
        try:
            user_api.get_user_course_detail(user_id, course_id)
            create_and_add_course_ff_and_custom_taxonomy_in_list(course_ff_custom_taxonomy, course_id)
        except:
            return feature_flags

    return feature_flags


def create_and_add_course_ff_and_custom_taxonomy_in_list(course_ff_custom_taxonomy, course_id):
    """
    append feature flag and custom taxonomy of required course in list
    """
    feature_flags, created = FeatureFlags.objects.get_or_create(course_id=course_id)
    course_meta_data, created = CourseMetaData.objects.get_or_create(course_id=course_id)
    course_ff_custom_taxonomy.append(
        {feature_flags.course_id: {"feature_flags": feature_flags.as_json(), "custom_taxonomy": course_meta_data.as_json()}})


def get_course_ff(user_id, feature_flag, course_id):
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
            create_and_add_course_ff_in_list(feature_flag, course_id)
        except:
            return feature_flags

    return feature_flags


def create_and_add_course_ff_in_list(feature_flag, course_id):
    """
    append feature flag of required course in list
    """
    feature_flags, created = FeatureFlags.objects.get_or_create(course_id=course_id)
    feature_flag.append({feature_flags.course_id: feature_flags.as_json()})

