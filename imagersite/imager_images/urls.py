"""."""
from django.conf.urls import url
from imager_images.views import library_view, photo_gallery_view

urlpatterns = [
    url(r'library$', library_view, name='library'),
    url(r'photos$', photo_gallery_view, name='photo_gallery')
]
