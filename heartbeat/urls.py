from django.conf.urls import url
from heartbeat import views as heartbeatviews


urlpatterns = [
    url(r'^$', heartbeatviews.heartbeat, name='heartbeat'),
]
