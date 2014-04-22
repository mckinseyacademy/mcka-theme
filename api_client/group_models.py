''' Objects for users / authentication built from json responses from API '''
from .json_object import JsonObject

class GroupInfo(JsonObject):
    ''' object representing a group from api json response '''
    required_fields = ["name", "id"]
