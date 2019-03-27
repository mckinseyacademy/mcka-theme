import os

from django.conf import settings
from django.template.loaders.cached import Loader
from hamlpy.template.loaders import HamlPyFilesystemLoader

from accounts.middleware import thread_local


NEW_UI_ADMIN_VIEWS = [
    'company_dashboard',
    'company_details',
    'company_course_details',
    'manager_dashboard',
]

OLD_UI_TEMPLATES = [
    'user_profile',
    'courses_menu'
]


def old_ui_for_admin_page(request):
    if '/admin' in request.path:
        if request.user.is_mcka_admin or request.user.is_internal_admin or request.user.is_mcka_subadmin:
            return True
        return request.resolver_match.view_name not in NEW_UI_ADMIN_VIEWS


class CustomLoader:
    def get_dirs(self):
        dirs = getattr(self, 'dirs', None) or self.engine.dirs
        request = thread_local.get_current_request()
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return dirs

        if thread_local.get_basic_user_data(request.user.id).get('new_ui_enabled'):
            if old_ui_for_admin_page(request) or request.resolver_match.view_name in OLD_UI_TEMPLATES:
                return dirs
            return settings.TEMPLATE_NEW_DIRS + dirs
        return dirs

    def get_template_dir(self, template_name):
        for path in self.get_dirs():
            if os.path.isfile(os.path.join(path, template_name)):
                return path


class CachedLoader(CustomLoader, Loader):
    def cache_key(self, template_name, template_dirs, skip=None):
        template_dirs = self.get_template_dir(template_name)
        return super(CachedLoader, self).cache_key(template_name, template_dirs)


class CustomHamlPyFilesystemLoader(CustomLoader, HamlPyFilesystemLoader):
    pass
