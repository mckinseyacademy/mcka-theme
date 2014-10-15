from datetime import datetime, timedelta
from django.utils import timezone
from django.db import models as db_models

class LessonNotesModel(db_models.Model):
    body = db_models.TextField()
    course_id = db_models.CharField(max_length=200, unique=False, db_index=True)
    lesson_id = db_models.CharField(max_length=200, unique=False, db_index=True)
    created_at = db_models.DateTimeField(auto_now_add=True)
    updated_at = db_models.DateTimeField(auto_now=True)
