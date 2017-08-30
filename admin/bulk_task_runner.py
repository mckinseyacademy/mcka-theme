"""
Handles running of different bulk tasks for admin
"""

from celery.result import AsyncResult

from .tasks import course_participants_data_retrieval_task, participants_notifications_data_task
from .controller import course_bulk_actions
from .models import BatchOperationStatus


class BulkTaskRunner(object):
    """
    Handles execution of bulk admin tasks
    """
    def __init__(self, request, params, task_name):
        """
        Args:
            self.request (object): HTTP self.request object
            params (dict):  params for the task
        """
        self.request = request
        self.params = params
        self.task_name = task_name

    def execute_task(self):
        """
        Executes the background tasks using celery or threaded tasks

        Returns:
            task_id (integer): task identifier to track the task
        """
        base_url = self.request.build_absolute_uri()
        company_id = self.params.get('company_id')
        course_id = self.params.get('course_id')

        if self.task_name == 'participants_csv_data':
            task_id = course_participants_data_retrieval_task.delay(
                course_id=course_id, company_id=company_id, base_url=base_url
            ).task_id
        elif self.task_name == 'push_notifications_data':
            task_id = participants_notifications_data_task.delay(
                course_id=course_id, company_id=company_id
            ).task_id
        else:
            # older functionality is still threaded tasks
            batch_status = BatchOperationStatus.create()
            task_id = batch_status.task_key
            course_bulk_actions(course_id, self.params, batch_status, self.request)

        return task_id

    @staticmethod
    def get_task_result(task_id):
        """
        Gets the result from a executed celery task
        """
        result = AsyncResult(id=task_id)

        return result.get() if result.ready() else []
