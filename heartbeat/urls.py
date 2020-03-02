from django.urls import path
from heartbeat import views as heartbeatviews


urlpatterns = [
    path('', heartbeatviews.heartbeat, name='heartbeat'),
]
