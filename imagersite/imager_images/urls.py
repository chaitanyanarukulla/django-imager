"""."""
from django.conf.urls import url
from imager_images import views
urlpatterns = [
    url(r'library$', views.LibraryView.as_view(), name='library'),
    url(r'photos$', views.PhotoGalleryView.as_view(), name='photo_gallery'),
    url(r'albums$', views.AlbumGalleryView.as_view(), name='album_gallery'),
    url(r'photos/(?P<id>\d+)$', views.PhotoDetailView.as_view(), name='photo_detail'),
    url(r'albums/(?P<id>\d+)$', views.AlbumDetailView.as_view(), name='album_detail'),
    url(r'photos/add$', views.PhotoCreateView.as_view(), name='photo_create'),
    url(r'albums/add$', views.AlbumCreateView.as_view(), name='album_create'),
    url(r'photos/(?P<id>\d+)/edit$', views.PhotoEditView.as_view(), name='photo_edit'),
    url(r'albums/(?P<id>\d+)/edit$', views.AlbumEditView.as_view(), name='album_edit')
]
