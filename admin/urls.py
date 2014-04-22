from django.conf.urls import patterns, url
from admin import views

urlpatterns = patterns(
    'admin',
    url(r'^$', views.home, name='admin_home'),
    url(r'^course_meta_content', views.course_meta_content, name='course_meta_content'),
    url(r'^not_authorized', views.not_authorized, name='not_authorized'),
    url(r'^clients/client_new', views.client_new, name='client_new'),
    url(r'^clients/(?P<client_id>.*)', views.client_detail, name='client_detail'),
    url(r'^clients', views.client_list, name='client_list'),
    url(r'^programs/program_new', views.program_new, name='program_new'),
    url(r'^programs/(?P<program_id>.*)', views.program_detail, name='program_detail'),
    url(r'^programs', views.program_list, name='program_list'),
)
