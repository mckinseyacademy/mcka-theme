from django.shortcuts import render


def terms(request):
    return render(request, 'terms.haml')


def privacy(request):
    return render(request, 'privacy.haml')
