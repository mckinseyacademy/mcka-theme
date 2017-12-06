from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.http import HttpResponseRedirect
from django.http import JsonResponse

from api_client.user_api import mark_user_notification_read

from .controller import get_android_app_manifest_json

def terms(request):
    return render(request, 'terms.haml')

def privacy(request):
    return render(request, 'privacy.haml')

def faq(request):
    return render(request, 'faq.haml')

def error_404(request):
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


def android_manifest_json(request, user_id):
    """
    This will return the json data which is needed for
     showing android native app banner.
    """
    manifest_json_file = get_android_app_manifest_json(user_id)

    return JsonResponse(manifest_json_file)
