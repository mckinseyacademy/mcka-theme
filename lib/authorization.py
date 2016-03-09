from functools import wraps
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.cache import cache
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.utils.decorators import available_attrs
from django.template import loader, RequestContext
from django.utils.http import urlquote

from api_client import user_api, group_api


def permission_groups_map():
    ''' Loads and caches group names and ids via the edX platform '''
    permission_groups_map = cache.get('permission_groups_map', None)
    if permission_groups_map is None:
        permission_groups = group_api.get_groups_of_type('permission')
        permission_groups_map = {permission_group.name: permission_group.id for permission_group in permission_groups}
        cache.set('permission_groups_map', permission_groups_map)

    return permission_groups_map


def is_user_in_permission_group(user, *group_names):
    for group_name in group_names:
        if group_name in permission_groups_map().keys():
            if user_api.is_user_in_group(user.id, permission_groups_map()[group_name]):
                return True

    return False


def permission_group_required(*group_names):
    ''' View decorator which requires user membership in
        at least one of the groups in a list of groups
    '''
    def decorator(view_fn):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated():
                if is_user_in_permission_group(request.user, *group_names):
                    return view_fn(request, *args, **kwargs)
                return permission_group_required_not_in_group(request)
            return permission_group_required_not_authenticated(request)
        return wraps(view_fn, assigned=available_attrs(view_fn))(_wrapped_view)
    return decorator


def permission_group_required_api(*group_names):
    ''' View decorator which requires user membership in
        at least one of the groups in a list of groups
    '''
    def decorator(view_fn):
        def _wrapped_view(self, request, *args, **kwargs):
            if request.user.is_authenticated():
                if is_user_in_permission_group(request.user, *group_names):
                    return view_fn(self, request, *args, **kwargs)
                return permission_group_required_not_in_group(request)
            return permission_group_required_not_authenticated(request)
        return wraps(view_fn, assigned=available_attrs(view_fn))(_wrapped_view)
    return decorator


def permission_group_required_not_in_group(request):
    template = loader.get_template('not_authorized.haml')
    context = RequestContext(request, {'request_path': request.path})
    return HttpResponseForbidden(template.render(context))


def permission_group_required_not_authenticated(request):
    path = urlquote(request.get_full_path())
    login_tuple = settings.LOGIN_URL, REDIRECT_FIELD_NAME, path
    return HttpResponseRedirect('%s?%s=%s' % login_tuple)