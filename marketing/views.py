''' rendering templates from requests related to marketing '''
from django.shortcuts import render
from django.template import TemplateDoesNotExist
from django.http import Http404
from lib.authorization import permission_group_required
from api_client.group_api import PERMISSION_GROUPS


def infer_default_navigation(request, page_name):
    page = "marketing/{0}.haml".format(page_name)
    try:
        return render(request, page)
    except TemplateDoesNotExist:
        raise Http404


@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN)
def styleguide(request):
    return render(request, 'styleguide.haml')
