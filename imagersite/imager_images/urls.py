"""."""
from django.conf.urls import url
from imager_images.views import library_view

urlpatterns = [
    url(r'library$', library_view, name='library')
]
