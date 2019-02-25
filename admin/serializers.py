from rest_framework import serializers
from admin.models import AdminTask


class AdminTaskSerializer(serializers.ModelSerializer):
    """
    Serializer for AdminTask model
    """

    url = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    parameters = serializers.JSONField(source='task_parameters')

    def get_name(self, admin_task):
        return admin_task.task_output.get('name')

    def get_url(self, admin_task):
        return admin_task.task_output.get('url')

    class Meta(object):
        model = AdminTask
        fields = (
            'task_id', 'course_id', 'parameters', 'task_type',
            'requested_datetime', 'status', 'url', 'name',
        )
