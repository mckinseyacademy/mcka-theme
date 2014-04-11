from django.shortcuts import render
from lib.authorization import group_required


@group_required('super_admin')
def home(request):
    return render(
        request,
        'admin/home.haml',
        {'is_admin': True}
    )


@group_required('super_admin')
def course_meta_content(request):
    return render(
        request,
        'admin/course_meta_content.haml',
        {'is_admin': True}
    )


def not_authorized(request):
    return render(request, 'admin/not_authorized.haml')
