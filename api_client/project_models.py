''' Objects for users / authentication built from json responses from API '''
import json
from datetime import datetime
from .json_object import JsonObject
from . import project_api, course_api


class Project(JsonObject):
    #required_fields = ["display_name", "contact_name", "contact_phone", "contact_email", ]

    def add_workgroup(self, workgroup_id):
        if workgroup_id not in self.workgroups:
            self.workgroups.add(workgroup_id)
            project_api.update_project(self.id, {"workgroups": self.workgroups})

    def remove_workgroup(self, workgroup_id):
        if workgroup_id in self.workgroups:
            self.workgroups.remove(workgroup_id)
            project_api.update_project(self.id, {"workgroups": self.workgroups})

    @classmethod
    def fetch(cls, project_id):
        return project_api.get_project(project_id, project_object=cls)

    @classmethod
    def list(cls, course_id, content_id):
        return project_api.get_all_projects(course_id, content_id, project_object=ProjectListResponse)

    @classmethod
    def fetch_from_url(cls, url):
        return project_api.fetch_project_from_url(url, project_object=cls)

    @classmethod
    def create(cls, course_id, content_id, organization_id=None):
        return project_api.create_project(course_id, content_id, organization_id, project_object=cls)

    @classmethod
    def fetch_projects_for_course(cls, course_id):
        return course_api.get_course_projects(course_id, project_object=cls)

    @classmethod
    def delete(cls, project_id):
        return project_api.delete_project(project_id)


class ProjectListResponse(JsonObject):
    object_map = {
        "results": Project
    }
