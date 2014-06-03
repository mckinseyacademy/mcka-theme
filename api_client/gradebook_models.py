''' Objects for course gradebooks built from json responses from API '''

from .json_object import DataOnly, JsonObject


class CourseSectionSummary(JsonObject):
    object_map = {
        "section_total": DataOnly,
        "scores": DataOnly,
    }


class GradeSummary(JsonObject):
    object_map = {
        "totaled_scores": DataOnly,
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
