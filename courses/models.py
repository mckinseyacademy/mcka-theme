from django.db import models as db_models


class LessonNotesItem(db_models.Model):
    body = db_models.TextField()
    user_id = db_models.IntegerField(unique=False, db_index=True, null=True)
    course_id = db_models.CharField(max_length=200, unique=False, db_index=True)
    lesson_id = db_models.CharField(max_length=200, unique=False, db_index=True)
    module_id = db_models.CharField(max_length=200, unique=False, db_index=True)
    created_at = db_models.DateTimeField(auto_now_add=True)
    updated_at = db_models.DateTimeField(auto_now=True)

    def as_csv(self, course):
        lesson = course.get_lesson(self.lesson_id)
        module = course.get_module(self.lesson_id, self.module_id)
        return [self.created_at, course.name, lesson.name, module.name, self.body]

    def as_json(self, course):
        lesson = course.get_lesson(self.lesson_id)
        module = course.get_module(self.lesson_id, self.module_id)

        return dict(
            id = self.id,
            body = self.body,
            course_id = self.course_id,
            course_name = course.name,
            lesson_id = self.lesson_id,
            lesson_index = lesson.index,
            lesson_name = lesson.name,
            lesson_navigation_url = lesson.navigation_url,
            module_id = self.module_id,
            module_index = module.index,
            module_name = module.name,
            module_navigation_url = module.navigation_url,
            created_at = self.created_at.isoformat(),
            updated_at = self.updated_at.isoformat(),
        )


class FeatureFlags(db_models.Model):
    course_id = db_models.CharField(max_length=200, unique=False, db_index=True)
    group_work = db_models.BooleanField(default=True)
    discussions = db_models.BooleanField(default=True)
    cohort_map = db_models.BooleanField(default=True)
    proficiency = db_models.BooleanField(default=True)
    progress = db_models.BooleanField(default=True)
    learner_dashboard = db_models.BooleanField(default=False)
    progress_page = db_models.BooleanField(default=True)
    notifications = db_models.BooleanField(default=True)
    branding = db_models.BooleanField(default=True)
    resources = db_models.BooleanField(default=True)
    cohort_avg = db_models.BooleanField(default=True)
    certificates = db_models.BooleanField(default=False)
    engagement = db_models.BooleanField(default=True)
    discover = db_models.BooleanField(default=True)

    def as_json(self):
        return dict(
            id=self.id,
            course_id=self.course_id,
            group_work=self.group_work,
            discussions=self.discussions,
            cohort_map=self.cohort_map,
            proficiency=self.proficiency,
            progress=self.progress,
            learner_dashboard=self.learner_dashboard,
            progress_page=self.progress_page,
            notifications=self.notifications,
            branding=self.branding,
            resources=self.resources,
            cohort_avg=self.cohort_avg,
            certificates=self.certificates,
            engagement=self.engagement,
            discover=self.discover,
        )


class CourseMetaData(db_models.Model):
    """
    This table is used to handle custom terminologies related to course.
    """
    course_id = db_models.CharField(max_length=200, unique=True, db_index=True)
    lesson_label = db_models.CharField(max_length=20, blank=True)
    module_label = db_models.CharField(max_length=20, blank=True)
    created_at = db_models.DateTimeField(auto_now_add=True)
    updated_at = db_models.DateTimeField(auto_now=True)

    def as_json(self):
        return dict(
            id=self.id,
            course_id=self.course_id,
            lesson_label=self.lesson_label,
            module_label=self.module_label,
        )

