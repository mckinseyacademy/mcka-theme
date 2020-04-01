from django.urls import path, re_path

from . import views

urlpatterns = [
    path('styleguide/', views.styleguide, name='styleguide'),
    path('contact/', views.contact, name='contact'),
    path('support/', views.support, name='support'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('edxoffer/', views.edxoffer, name='edxoffer'),
    re_path(r'fblf/$(?i)', views.fblf, name='fblf'),
    re_path(r'^(?P<page_name>.*)/$', views.infer_default_navigation, name='infer_default_navigation'),
]
