"""."""
from django.conf.urls import url
from imager_images import views
urlpatterns = [
    url(r'library$', views.library_view, name='library'),
    url(r'photos$', views.photo_gallery_view, name='photo_gallery'),
    url(r'albums$', views.album_gallery_view, name='album_gallery'),
    url(r'photos/(?P<id>\d+)$', views.photo_detail_view, name='photo_detail'),
    url(r'albums/(?P<id>\d+)$', views.album_detail_view, name='album_detail')
]
