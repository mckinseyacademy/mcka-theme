''' Objects for course gradebooks built from json responses from API '''

from .json_object import DataOnly, JsonObject, CategorisedJsonObject


class CourseSectionSummary(JsonObject):
    object_map = {
        "section_total": DataOnly,
        "scores": DataOnly,
    }


class GradeSummary(JsonObject):
    object_map = {
        "section_breakdown": CategorisedJsonObject,
        "totaled_scores": DataOnly,
        "grade_breakdown": CategorisedJsonObject
    }


class CourseSummary(JsonObject):
    object_map = {
        "sections": CourseSectionSummary
    }


class Gradebook(JsonObject):
    object_map = {
        "courseware_summary": CourseSummary,
        "grade_summary": GradeSummary
    }
