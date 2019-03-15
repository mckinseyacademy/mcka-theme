import os

from django.conf import settings
from django.template.loaders.cached import Loader
from hamlpy.template.loaders import HamlPyFilesystemLoader

from accounts.middleware import thread_local
from api_data_manager.organization_data import OrgDataManager
from api_data_manager.user_data import UserDataManager


NEW_UI_ADMIN_VIEWS = [
    'company_dashboard',
    'company_details',
    'company_course_details',
    'manager_dashboard',
]


def old_ui_for_admin_page(request):
    if '/admin' in request.path:
        if request.user.is_mcka_admin or request.user.is_internal_admin or request.user.is_mcka_subadmin:
            return True
        return request.resolver_match.view_name not in NEW_UI_ADMIN_VIEWS


def get_customization(request):
    organization = UserDataManager(str(request.user.id)).get_basic_user_data().get('organization')
    if not organization:
        return
    return OrgDataManager(str(organization.id)).get_branding_data().get('customization')


class CustomLoader:
    def get_dirs(self):
        dirs = getattr(self, 'dirs', None) or self.engine.dirs
        request = thread_local.get_current_request()
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return dirs

        client_customizations = get_customization(request)
        if client_customizations and client_customizations.new_ui_enabled:
            if old_ui_for_admin_page(request):
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
