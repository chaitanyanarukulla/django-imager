from django.conf.urls import url
from imager_api.views import PhotoListAPI

urlpatterns = [
    url(r'^photos/$', PhotoListAPI.as_view(), name='api_photo_list'),
]
