from django.apps import AppConfig


class CoursesConfig(AppConfig):
    name = 'courses'
    label = 'courses'

    def ready(self):
        import courses.signals  # noqa: F401
