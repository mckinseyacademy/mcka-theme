from django.conf import settings


def show_toolbar(request):
    """
    Default function to determine whether to show the toolbar for a given user. For Apros we can enable the showing
    of the Django Debug Toolbar by a SHOW_DEBUG_TOOLBAR_ALL_IPS=True in the local settings file to ingore list
    explicit list of INTERNAL_IPS
    """

    show_debug_toolbar_all_ips = getattr(settings, 'SHOW_DEBUG_TOOLBAR_ALL_IPS', False)

    if request.META.get('REMOTE_ADDR', None) not in settings.INTERNAL_IPS:
        if not show_debug_toolbar_all_ips:
            return False

    if request.GET.get('ddt') == 'enable':
        request.session['ddt'] = True

    # never return DjDT on an Ajax call, except for djDT calls itself
    if request.is_ajax():
        if request.GET.get('panel_id'):
            return True

        return False

    # staff can see this if the session flag is set
    if request.user and request.user.is_staff and request.session.get('ddt', False):
        return True

    # always show DjDT when in Debug mode (and not servicing a Ajax request)
    return bool(settings.DEBUG)
