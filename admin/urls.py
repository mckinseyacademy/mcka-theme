from django.conf.urls import patterns, url
from admin import views

urlpatterns = patterns('admin',
    url(r'^$', views.home, name='admin_home'),
    url(r'^course_meta_content', views.course_meta_content, name='course_meta_content'),
)
