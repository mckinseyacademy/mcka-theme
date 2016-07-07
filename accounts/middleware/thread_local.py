''' globally available request object  '''
import threading
from django.core.cache import cache
import json
_threadlocal = threading.local()


class ThreadLocal(object):

    def process_request(self, request):
        _threadlocal.request = request
        _threadlocal.current_course = None
        _threadlocal.static_tabs = None
        _threadlocal.user_permissions = None

    def process_response(self, request, response):
        _threadlocal.request = None
        _threadlocal.current_course = None
        _threadlocal.static_tabs = None
        _threadlocal.user_permissions = None
        return response


def get_current_request():
    return getattr(_threadlocal, 'request', None)


def set_course_context(course, depth):
    setattr(_threadlocal, 'current_course', {
            "course_id": course.id,
            "course_content": course,
            "depth": depth
        }
    )


def get_course_context():
    return getattr(_threadlocal,  'current_course', None)

def set_static_tab_context(course_id, static_tab_dictionary, name=None):
    if name:
        static_tabs = get_static_tab_context(course_id)
        if not static_tabs:
            static_tabs = dict()
        if name in static_tabs.keys():
            static_tabs[name] = static_tab_dictionary
        setattr(_threadlocal, 'static_tabs', 
            [{'course_id': course_id, 
            'static_tabs_list': static_tabs}]
        )
    else:
        setattr(_threadlocal, 'static_tabs', 
            [{'course_id': course_id, 
            'static_tabs_list': static_tab_dictionary}]
        )

def get_static_tab_context(course_id, name=None, tab_id=None):
    if name:
        static_tabs = getattr(_threadlocal, 'static_tabs', None)
        if static_tabs: 
            static_tabs_list = [static_tab['static_tabs_list'] for static_tab in static_tabs if static_tab['course_id'] == course_id][0]        
        if name in static_tabs_list.keys():
            return static_tabs_list[name]
        return None

    static_tabs = getattr(_threadlocal, 'static_tabs', None)
    if static_tabs:
        temp_tabs = [static_tab['static_tabs_list'] for static_tab in static_tabs if static_tab['course_id'] == course_id]
        if len(temp_tabs):
            static_tabs_list = temp_tabs[0]
            return static_tabs_list
    return None

def set_user_permissions_context(permissions = None):
    if permissions:
        setattr(_threadlocal, 'user_permissions', permissions)
    else:
        setattr(_threadlocal, 'user_permissions', None)

def get_user_permissions_context():
    return getattr(_threadlocal, 'user_permissions', None)


def get_user_permissions(user):
    ''' Loads and caches group names and ids via the edX platform '''
    from api_client import user_api, group_api
    from api_client.group_api import PERMISSION_GROUPS, PERMISSION_TYPE
    permissions_data = {"global_permissions":[],"organization_permissions":[]}
    permission_groups = group_api.get_groups_of_type(PERMISSION_TYPE)
    permission_dict = {permission_group.name: permission_group.id for permission_group in permission_groups}
    current_permissions = [pg.name for pg in user_api.get_user_groups(user.id, PERMISSION_TYPE)]
    for perm in current_permissions:
        if perm not in (PERMISSION_GROUPS.MCKA_TA, PERMISSION_GROUPS.MCKA_OBSERVER):
            permissions_data["global_permissions"].append({perm: permission_dict[perm]})
    
    global_permissions = [{perm: permission_dict[perm]} for perm in current_permissions if perm not in (PERMISSION_GROUPS.MCKA_TA, PERMISSION_GROUPS.MCKA_OBSERVER)]
    return permissions_data
