import time

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.core.cache import cache
from .models import Program
from api_client import user_api, group_api, course_api, organization_api
from api_client.user_api import USER_ROLES
from api_client.group_api import PERMISSION_GROUPS, PERMISSION_TYPE

CACHE_EXPIRE_TIME = 3600

class course_list_cached_api(APIView):
    def get(self, request):
        force_new = request.GET.get('force_refresh', None)
        program_id = request.GET.get('program_id', None)
        data_format = request.GET.get('data_format', None)
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
        course_list_response = []
        if program_id:
            program = Program.fetch(program_id)
            selected_ids = [course.course_id for course in program.fetch_courses()]
        for course in course_list:
            course.name = (course.name[:max_string_length] + '...') if len(course.name) > max_string_length else course.name
            data = {"name":course.name, "id":course.id, "value":course.id, "start":course.start, "end":course.end, "due":course.due}
            if program_id:
                data["additional_class"] = "selected" if course.id in selected_ids else ""
                data["in_program"] = True if data["additional_class"] == "selected" else False
            if data_format == "table":
                data["table_data"] = [course.name, course.id]
                data["row_ids"] = course.id
            course_list_response.append(data)
        return Response(course_list_response)