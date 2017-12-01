"""."""
from django.conf.urls import url
from imager_images.views import library_view, photo_gallery_view, album_gallery_view

urlpatterns = [
    url(r'library$', library_view, name='library'),
    url(r'photos$', photo_gallery_view, name='photo_gallery'),
    url(r'albums$', album_gallery_view, name='album_gallery')
]
