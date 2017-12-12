from django.conf.urls import url
from imager_api.views import PhotoList

urlpatterns = [
    url(r'^photos/$', PhotoList.as_view()),
]
