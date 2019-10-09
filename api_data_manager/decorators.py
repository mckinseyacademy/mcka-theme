from functools import wraps
from django.utils.decorators import available_attrs
from django.utils.translation import ugettext as _

from .user_data import UserDataManager, USER_PROPERTIES
from .group_data import GroupDataManager
from .course_data import CourseDataManager, COURSE_PROPERTIES

COURSE_DEFAULT_DEPTH = 3


def user_api_cache_wrapper(parse_method, property_name, parse_object=None, post_process_method=None):
    def decorator(view_fn):
        def _wrapped_view(*args, **kwargs):
            data_property = property_name
            try:
                user_id = args[0]
            except IndexError:
                user_id = kwargs.get('user_id')

            if not user_id:
                raise ValueError(_('User Id is not passed'))

            cache_identifiers = []
            skip_caching = False

            if data_property in (USER_PROPERTIES.USER_COURSE_DETAIL, USER_PROPERTIES.USER_COURSE_WORKGROUPS):
                try:
                    course_id = args[1]
                except IndexError:
                    course_id = kwargs.get('course_id')

                if not course_id:
                    raise ValueError(_('Course Id is not passed'))

                cache_identifiers.append(course_id)

            if data_property == USER_PROPERTIES.GROUPS:
                group_type = kwargs.get('group_type')
                course_id = kwargs.get('course')
                xblock_id = kwargs.get('data__xblock_id')

                if group_type:
                    cache_identifiers.append(group_type)

                if course_id:
                    cache_identifiers.append(course_id)

                if xblock_id:
                    skip_caching = True
                    cache_identifiers.append(xblock_id)

            if skip_caching:
                data = view_fn(*args, **kwargs)
            else:
                user_data_manager = UserDataManager(user_id, identifiers=cache_identifiers)
                data = user_data_manager.get_cached_data(data_property)

                if data is None:
                    data = view_fn(*args, **kwargs)
                    user_data_manager.set_cached_data(data_property, data)

            object_parser = kwargs.get('parse_object') or parse_object
            if type(data) is bytes:
                data = data.decode('utf-8')

            if object_parser:
                parsed_data = parse_method(data, object_parser)
            else:
                parsed_data = parse_method(data)

            return post_process_method(parsed_data) if post_process_method else parsed_data

        return wraps(view_fn, assigned=available_attrs(view_fn))(_wrapped_view)

    return decorator


def group_api_cache_wrapper(parse_method, parse_object, property_name, post_process_method=None):
    def decorator(view_fn):
        def _wrapped_view(*args, **kwargs):
            data_property = property_name
            try:
                group_id = args[0]
            except IndexError:
                group_id = kwargs.get('group_id')

            if not group_id:
                raise ValueError(_('Group Id is not passed'))

            group_data_manager = GroupDataManager(group_id)

            data = group_data_manager.get_cached_data(data_property)

            if data is None:
                data = view_fn(*args, **kwargs)
                group_data_manager.set_cached_data(data_property, data)

            object_parser = kwargs.get('parse_object') or parse_object

            if object_parser:
                parsed_data = parse_method(data, object_parser)
            else:
                parsed_data = parse_method(data)

            return post_process_method(parsed_data) if post_process_method else parsed_data

        return wraps(view_fn, assigned=available_attrs(view_fn))(_wrapped_view)

    return decorator


def course_api_cache_wrapper(parse_method, parse_object, property_name, post_process_method=None):
    def decorator(view_fn):
        def _wrapped_view(*args, **kwargs):
            data_property = property_name

            try:
                course_id = args[0]
            except IndexError:
                course_id = kwargs.get('course_id')

            if not course_id:
                raise ValueError(_('Course Id is not passed'))

            if data_property == COURSE_PROPERTIES.TABS:
                if kwargs.get('details'):
                    data_property = '{}_{}'.format(data_property, 'details')

            if data_property == COURSE_PROPERTIES.TAB_CONTENT:
                try:
                    tab_id = kwargs['tab_id']
                    data_property = '{}_{}'.format(data_property, tab_id)
                except KeyError:
                    tab_name = kwargs['name']
                    data_property = '{}_{}'.format(data_property, tab_name)

            elif data_property == COURSE_PROPERTIES.DETAIL:
                tree_depth = kwargs.get('depth')

                if tree_depth is None:
                    try:
                        tree_depth = args[1]
                    except IndexError:
                        tree_depth = COURSE_DEFAULT_DEPTH

                # Sometimes this API retrieves different course trees for different users
                # (e.g. staff users can see staff-only sections)
                # For the sake of optimization, as course details api is a heavy call, for now
                # the cache maintains JUST TWO type of responses of course details API
                # one for staff users and one for all normal users
                # change this implementation if we need to get per-user course tree
                user_type = 'staff'
                try:
                    user = args[2]
                except IndexError:
                    user = kwargs.get('user')

                if user:  # User may be an object or a dict.
                    from api_client import course_api
                    user_id, is_superuser = None, False
                    try:
                        user_id, is_superuser = user.id, user.is_staff
                    except AttributeError:
                        user_id, is_superuser = user.get('id'), user.get('is_staff')

                    if is_superuser:
                        user_type = 'staff'
                    else:
                        roles = course_api.get_users_filtered_by_role(course_id)
                        user_roles = {r.role for r in roles if r.id == user_id}
                        user_type = 'staff' if {'instructor', 'staff'} & user_roles else 'generic'

                data_property = '{}_{}_{}'.format(data_property, tree_depth, user_type)

            course_data_manager = CourseDataManager(course_id)

            data = course_data_manager.get_cached_data(data_property)

            if data is None:
                data = view_fn(*args, **kwargs)
                course_data_manager.set_cached_data(data_property, data)

            object_parser = kwargs.get('parse_object') or parse_object

            if object_parser:
                parsed_data = parse_method(data, object_parser)
            else:
                parsed_data = parse_method(data)

            return post_process_method(parsed_data) if post_process_method else parsed_data

        return wraps(view_fn, assigned=available_attrs(view_fn))(_wrapped_view)

    return decorator
