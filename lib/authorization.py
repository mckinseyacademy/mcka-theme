from django.core.cache import cache
from django.contrib.auth.decorators import user_passes_test
from api_client import user_api


def load_groups():
    ''' Loads and caches group names and ids via the edX platform '''
    groups_map = user_api.get_groups()
    cache.set('edx_groups_map', groups_map)
    return groups_map


def group_required(*group_names):
    ''' Requires user membership in at least one of the groups passed in '''
    groups_map = cache.get('edx_groups_map', load_groups())
    def in_groups(u):
        if u.is_authenticated():
            for group_name in group_names:
                if group_name in groups_map.keys():
                    return user_api.is_user_in_group(u.id, groups_map[group_name])
        return False
    return user_passes_test(in_groups)