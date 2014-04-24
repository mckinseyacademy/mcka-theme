from api_client import group_api
from api_client import group_models


class BaseGroupModel(group_models.GroupInfo):

    def __init__(self, json_data=None, dictionary=None):
        super(BaseGroupModel, self).__init__(
            json_data=json_data,
            dictionary=dictionary
        )

        if not hasattr(self, "id") and hasattr(self, "group_id"):
            self.id = self.group_id

        if not hasattr(self, "name") and hasattr(self, "display_name"):
            self.name = self.display_name

    def __unicode__(self):
        return self.name


class Client(BaseGroupModel):
    data_fields = ["display_name", "contact_name", "phone", "email", ]
    group_type = "organization"


class Program(BaseGroupModel):
    data_fields = ["display_name", "start_date", "end_date", ]
    date_fields = ["start_date", "end_date"]
    group_type = "series"
