''' rendering templates from requests related to marketing '''
from django.shortcuts import render
from lib.authorization import group_required


def infer_default_navigation(request, page_name):
    page = "marketing/{0}.haml".format(page_name)
    return render(request, page)


@group_required('super_admin')
def styleguide(request):
    return render(request, 'styleguide.haml')
