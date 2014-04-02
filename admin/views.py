from django.shortcuts import render


def home(request):
    ''' show me the admin home page '''

    return render(request, 'admin/home.haml')

def course_meta_content(request):
    ''' show me the admin home page '''

    return render(request, 'admin/home.haml')
