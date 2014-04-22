''' Objects for administration built from json responses from API '''
from .json_object import JsonObject

class Program(JsonObject):
    ''' object representing a group from api json response '''
    required_fields = ["name", "id"]
    date_fields = ["start_date", "end_date"]
