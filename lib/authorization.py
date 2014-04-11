from functools import wraps
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.cache import cache
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.utils.decorators import available_attrs
from django.template import loader, RequestContext
from django.utils.http import urlquote

from api_client import user_api


def load_groups():
    ''' Loads and caches group names and ids via the edX platform '''
    groups_map = user_api.get_groups()
    cache.set('edx_groups_map', groups_map)

    return groups_map


def is_user_in_group(user, *group_names):
    groups_map = cache.get('edx_groups_map', load_groups())
    for group_name in group_names:
        if group_name in groups_map.keys():
            return user_api.is_user_in_group(user.id, groups_map[group_name])
    return False


def group_required(*group_names):
    ''' View decorator which requires user membership in
        at least one of the groups in a list of groups
    '''
    def decorator(view_fn):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated():
                if is_user_in_group(request.user, *group_names):
                    return view_fn(request, *args, **kwargs)
                template = loader.get_template('not_authorized.haml')
                context = RequestContext(request, {'request_path': request.path})
                return HttpResponseForbidden(template.render(context))
            path = urlquote(request.get_full_path)
            login_tuple = settings.LOGIN_URL, REDIRECT_FIELD_NAME, path
            return HttpResponseRedirect('%s?%s=%s' % login_tuple)
        return wraps(view_fn, assigned=available_attrs(view_fn))(_wrapped_view)
    return decorator
