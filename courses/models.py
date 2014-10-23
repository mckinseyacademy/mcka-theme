from datetime import datetime, timedelta
from django.utils import timezone
from django.db import models as db_models

class LessonNotesItem(db_models.Model):
    body = db_models.TextField()
    user_id = db_models.IntegerField(unique=False, db_index=True, null=True)
    course_id = db_models.CharField(max_length=200, unique=False, db_index=True)
    lesson_id = db_models.CharField(max_length=200, unique=False, db_index=True)
    created_at = db_models.DateTimeField(auto_now_add=True)
    updated_at = db_models.DateTimeField(auto_now=True)

    def as_json(self):
        return dict(
            id = self.id,
            body = self.body,
            course_id = self.course_id,
            lesson_id = self.lesson_id,
            created_at = self.created_at.isoformat(),
            updated_at = self.updated_at.isoformat(),
        )
