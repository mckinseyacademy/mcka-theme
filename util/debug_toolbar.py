from django.conf import settings

def show_toolbar(request):
    """
    Default function to determine whether to show the toolbar on a given page. For Apros we can enable the showing of the Django Debug Toolbar
    by a SHOW_DEBUG_TOOLBAR_ALL_IPS=True in the local settings file to ingore list explicit list of INTERNAL_IPS
    """

    show_debug_toolbar_all_ips = getattr(settings, 'SHOW_DEBUG_TOOLBAR_ALL_IPS', False)

    if request.META.get('REMOTE_ADDR', None) not in settings.INTERNAL_IPS:
        if not show_debug_toolbar_all_ips:
            return False

    if request.is_ajax():
        return False

    return bool(settings.DEBUG)
