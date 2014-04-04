from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from lib.authorization import group_required


@group_required('super_admin')
def home(request):
    return render(request, 'admin/home.haml')


@group_required('super_admin')
def course_meta_content(request):
    return render(request, 'admin/course_meta_content.haml')
