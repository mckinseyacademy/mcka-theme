from django.shortcuts import render

def terms(request):
    return render(request, 'terms.haml')

def privacy(request):
    return render(request, 'privacy.haml')

def faq(request):
    return render(request, 'faq.haml')

def error_404(request):
    return render(request, '404.haml')

def error_500(request):
    return render(request, '500.haml')
