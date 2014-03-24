from json_object import JsonObject

import hashlib

# Create your models here.


class UserResponse(JsonObject):
    required_fields = ["email", "username"]

    def image_url(self, size=40):
        return "http://www.gravatar.com/avatar/" + hashlib.md5(self.email.lower()).hexdigest() + "?s={}".format(size)

    def formatted_name(self):
        return "{} {}".format(self.first_name, self.last_name)


class AuthenticationResponse(JsonObject):
    required_fields = ['token', 'user']
    object_map = {
        "user": UserResponse
    }

class UserCourseBookmark(JsonObject):
    required_fields = ["chapter_id", "page_id"]

class UserCourseStatus(JsonObject):
    required_fields = ["course_id", "percent_complete"]
    object_map = {
        "bookmark": UserCourseBookmark
    }

class UserStatus(JsonObject):
    required_fields = []
    object_map = {
        "courses": UserCourseStatus
    }

    def get_bookmark_for_course(self, course_id):
        for course_status in self.courses:
            if course_status.course_id == course_id and None != course_status.bookmark:
                return course_status.bookmark

        return None

