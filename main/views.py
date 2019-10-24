from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import Http404
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.views.generic.base import View
from django.utils.translation import ugettext as _
from django.utils.translation import LANGUAGE_SESSION_KEY
from django.core.files.storage import default_storage
from django.conf import settings

import urllib.request
import urllib.parse
import urllib.error
from mimetypes import MimeTypes

from api_client.user_api import mark_user_notification_read
from util.s3_helpers import PrivateMediaStorageThroughApros

LANGUAGE_INPUT_FIELD = 'preview_lang'


def terms(request):
    return render(request, 'terms.haml')


def privacy(request):
    return render(request, 'privacy.haml')


def faq(request):
    return render(request, 'faq.haml')


def getting_started(request):
    return render(request, 'getting-started.haml')


def error_403(request, exception):
    return render(request, '403.haml', status=403)


def error_404(request, exception):
    return render(request, '404.haml', status=404)


def error_500(request):
    return render(request, '500.haml', status=500)


@login_required
def notification_redir(request):
    """
    This is used when a notification digest email is clicked on and we need to
    a) mark the notification as read and b) redirect to the right URL
    """

    redir_path = request.GET.get('redirect_path')
    msg_id = request.GET.get('msg_id')

    if not redir_path or not msg_id:
        raise Http404

    # Apros wants clicked through notifications from emails and digests
    # to mark the notification as read
    mark_user_notification_read(request.user.id, msg_id, read=True)

    return HttpResponseRedirect(redir_path)


class PreviewLanguageView(View):
    """
    View used when a user is attempting to change the preview language.

    GET - returns a form for setting/resetting the user's language
    POST - updates or clears the setting to the given language
    """
    template_name = 'preview_language.haml'

    @method_decorator(login_required)
    def get(self, request):
        """
        Returns the Form for setting/resetting a User's language setting
        """
        return render(request, self.template_name)

    @method_decorator(login_required)
    def post(self, request):
        """
        Sets or clears the language depending on the incoming post data.
        """
        message = None
        show_refresh_message = False
        context = dict()
        if 'set_language' in request.POST:
            # Set the Preview Language
            preview_lang = request.POST.get(LANGUAGE_INPUT_FIELD, '')
            if not preview_lang.strip():
                message = _('Language code not provided')
            else:
                # Set the session key to the requested preview lang
                request.session[LANGUAGE_SESSION_KEY] = preview_lang
                message = _('Language set to language code: {preview_language_code}').format(
                    preview_language_code=preview_lang
                )
                show_refresh_message = True
        elif 'reset' in request.POST:
            # Reset and clear the language preference
            if LANGUAGE_SESSION_KEY in request.session:
                del request.session[LANGUAGE_SESSION_KEY]

            message = _("Language reset to default language")
            show_refresh_message = True

        context.update({'message': message})
        context.update({'success': show_refresh_message})

        return render(request, self.template_name, context)


@login_required
def private_storage_access(request, path):
    """
    Endpoint to access private files on storage. Requires
    authenticated user with necessary permissions
    """
    if settings.DEFAULT_FILE_STORAGE == 'storages.backends.s3boto.S3BotoStorage':
        storage = PrivateMediaStorageThroughApros()

        if not storage.can_access(user=request.user, file_name=path):
            return HttpResponseForbidden()
    else:
        storage = default_storage

    if storage.exists(path):
        resource = storage.open(path).read()
        mime = MimeTypes()
        url = urllib.request.pathname2url(path)
        mime_type = mime.guess_type(url)

        return HttpResponse(
            resource, content_type=mime_type[0]
        )
    else:
        raise Http404
