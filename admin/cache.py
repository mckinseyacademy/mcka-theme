import time

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.core.cache import cache
from api_client import user_api, group_api, course_api, organization_api
from api_client.user_api import USER_ROLES
from api_client.group_api import PERMISSION_GROUPS, PERMISSION_TYPE

CACHE_EXPIRE_TIME = 3600

class course_list_cached_api(APIView):
    def get(self, request):
        force_new = request.GET.get('force_refresh', None)
        course_list = cache.get('course_list_cached', None)
        time_now = time.time()
        if course_list is None or force_new:
            course_list = course_api.get_course_list()
            cache.set('course_list_cached', course_list)
            time_now = time.time()
            cache.set('course_list_cached_last_update_time', time_now)
        else:
            course_list_last_update_time = cache.get('course_list_cached_last_update_time', None)
            if course_list_last_update_time:
                if time_now - course_list_last_update_time > CACHE_EXPIRE_TIME:
                    course_list = course_api.get_course_list()
                    cache.set('course_list_cached', course_list)
                    cache.set('course_list_cached_last_update_time', time_now)
            else:
                cache.set('course_list_cached_last_update_time', time_now)

        max_string_length = 75
        for course in course_list:
            course.name = (course.name[:max_string_length] + '...') if len(course.name) > max_string_length else course.name

        return Response([{"name":course.name, "id":course.id, "value":course.id, "start":course.start, "end":course.end, "due":course.due} for course in course_list])