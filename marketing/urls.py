from django.conf.urls import include, patterns, url

from marketing import views

urlpatterns = patterns(
    '',
    url(r'^styleguide', views.styleguide, name='styleguide'),
    #url(r'^', views.infer_default_navigation, name='infer_default_navigation'),
)
