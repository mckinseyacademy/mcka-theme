from functools import wraps
from django.utils.decorators import available_attrs


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
                raise ValueError('User Id is not passed')
            
            cache_identifiers = []
            skip_caching = False

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
                raise ValueError('Group Id is not passed')

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


def course_api__cache_wrapper(parse_method, parse_object, property_name, post_process_method=None):
    def decorator(view_fn):
        def _wrapped_view(*args, **kwargs):
            data_property = property_name

            try:
                course_id=args[0]
            except IndexError:
                course_id = kwargs.get('course_id')

            if not course_id:
                raise ValueError('Course Id is not passed')

            if data_property == COURSE_PROPERTIES.DETAIL:
                tree_depth = kwargs.get('depth')

                if tree_depth is None:
                    try:
                        tree_depth = args[1]
                    except IndexError:
                        tree_depth = COURSE_DEFAULT_DEPTH

                data_property = '{}_{}'.format(data_property, tree_depth)

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