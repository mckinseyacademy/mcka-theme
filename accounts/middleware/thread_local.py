''' globally available request object  '''
import threading

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


def set_static_tab_context(course_tabs):
    setattr(_threadlocal, 'course_tabs', course_tabs)


def get_static_tab_context():
    return getattr(_threadlocal, 'course_tabs', None)


def set_user_permissions_context(permissions=None):
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
    permissions_data = {"global_permissions": [], "organization_permissions": []}
    permission_groups = group_api.get_groups_of_type(PERMISSION_TYPE)
    permission_dict = {permission_group.name: permission_group.id for permission_group in permission_groups}
    current_permissions = [pg.name for pg in user_api.get_user_groups(user.id, PERMISSION_TYPE)]
    for perm in current_permissions:
        if perm not in (PERMISSION_GROUPS.MCKA_TA, PERMISSION_GROUPS.MCKA_OBSERVER):
            permissions_data["global_permissions"].append({perm: permission_dict[perm]})

    return permissions_data
