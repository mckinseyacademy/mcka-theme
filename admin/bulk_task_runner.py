"""
Handles running of different bulk tasks for admin
"""

from celery.result import AsyncResult
from upload_validator import FileTypeValidator

from .tasks import (
    course_participants_data_retrieval_task, participants_notifications_data_task,
    users_program_association_task
)
from .controller import (
    course_bulk_actions, build_student_list_from_file,
    participant_csv_line_id_extractor
)
from .models import BatchOperationStatus


class BulkTaskRunner(object):
    """
    Handles execution of bulk admin tasks
    """
    def __init__(self, request, params, task_name):
        """
        Args:
            self.request (object): HTTP request object
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
            lesson_completions = self.params.get('lesson_completions', False)

            task_id = _execute_participants_data_task(
                course_id, company_id, base_url,
                lesson_completions, user_id=self.request.user.id
            )
        elif self.task_name == 'push_notifications_data':
            task_id = _execute_notifications_data_task(course_id, company_id)
        elif self.task_name == 'user_program_association':
            task_id = _execute_users_program_association_task(
                self.request.FILES.get('participants_file'),
                self.params.get('program_id')
            )
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

    @staticmethod
    def get_task_state(task_id):
        """
        Gets the state of a task
        """
        result = AsyncResult(task_id)

        return result.state, result.info


def _execute_participants_data_task(course_id, company_id, base_url, lesson_completions, user_id):
    """
    Executes the csv data task
    """
    return course_participants_data_retrieval_task.delay(
        course_id=course_id, company_id=company_id, base_url=base_url,
        lesson_completions=lesson_completions, user_id=user_id
    ).task_id


def _execute_notifications_data_task(course_id, company_id):
    """
    Executes the notifications data task
    """
    return participants_notifications_data_task.delay(
        course_id=course_id, company_id=company_id
    ).task_id


def _execute_users_program_association_task(participants_file, program_id):
    """
    Executes the users-program association task
    """

    # validate file is a csv/text file
    validator = FileTypeValidator(allowed_types=['text/plain', 'text/csv'])
    try:
        validator(participants_file)
    except Exception as e:
        e.message = e.message % e.params
        raise

    user_ids = build_student_list_from_file(
        participants_file, parse_method=participant_csv_line_id_extractor
    )

    return users_program_association_task.delay(
        program_id=program_id, user_ids=user_ids
    ).task_id
