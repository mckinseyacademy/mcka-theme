from json_object import JsonObject

import hashlib

# Create your models here.

class Page(JsonObject):
    required_fields = []

class Chapter(JsonObject):
    required_fields = []
    object_map = {
        "pages" : Page,
    }

class Course(JsonObject):
    required_fields = []
    object_map = {
        "chapters" : Chapter,
    }

class PageContent(JsonObject):
    required_fields = []
