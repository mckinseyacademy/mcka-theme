from django.shortcuts import render


def home(request):
    return render(request, 'admin/home.haml')


def course_meta_content(request):
    return render(request, 'admin/course_meta_content.haml')
