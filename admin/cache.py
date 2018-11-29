from rest_framework.views import APIView
from rest_framework.response import Response

from django.core.cache import cache
from .models import Program
from api_client import course_api, organization_api

CACHE_EXPIRE_TIME = 3600


class course_list_cached_api(APIView):
    def get(self, request):
        force_new = request.GET.get('force_refresh', None)
        program_id = request.GET.get('program_id', None)
        data_format = request.GET.get('data_format', None)

        if force_new:
            course_list = course_api.get_course_list()
        else:
            cache_expire = request.GET.get('cache_expire', CACHE_EXPIRE_TIME)
            course_list = cache.get('course_list_cached', None)

            if course_list is None:
                course_list = course_api.get_course_list()
                cache.set('course_list_cached', course_list, cache_expire)

        max_string_length = 75
        course_list_response = []
        if program_id:
            program = Program.fetch(program_id)
            selected_ids = [course.course_id for course in program.fetch_courses()]
        for course in course_list:
            course.name = (course.name[:max_string_length] + '...') if len(course.name) > max_string_length \
                else course.name
            data = {"name": course.name, "id": course.id, "value": course.id, "start": course.start, "end": course.end,
                    "due": course.due}
            if program_id:
                data["additional_class"] = "selected" if course.id in selected_ids else ""
                data["in_program"] = True if data["additional_class"] == "selected" else False
            if data_format == "table":
                data["table_data"] = [course.name, course.id]
                data["row_ids"] = course.id
            course_list_response.append(data)

        return Response(course_list_response)


class organizations_list_cached_api(APIView):
    def get(self, request):
        force_new = request.GET.get('force_refresh', None)

        if force_new:
            organizations_list = organization_api.get_organizations_dict()
        else:
            cache_expire = request.GET.get('cache_expire', CACHE_EXPIRE_TIME)
            organizations_list = cache.get('organizations_list_cached', None)

            if organizations_list is None:
                organizations_list = organization_api.get_organizations_dict()
                cache.set('organizations_list_cached', organizations_list, cache_expire)

        return Response(organizations_list)


class organization_courses_cached_api(APIView):
    def get(self, request, organization_id):
        if organization_id:
            force_new = request.GET.get('force_refresh', None)

            if force_new:
                organization_courses = organization_api.get_organizations_courses(organization_id)
            else:
                organization_courses = cache.get('organization_{}_cached'.format(organization_id), None)
                cache_expire = request.GET.get('cache_expire', CACHE_EXPIRE_TIME)

                if organization_courses is None:
                    organization_courses = organization_api.get_organizations_courses(organization_id)
                    cache.set('organization_{}_cached'.format(organization_id), organization_courses, cache_expire)

            return Response(organization_courses)

        return Response(organization_courses)
