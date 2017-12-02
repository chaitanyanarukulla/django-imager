"""."""
from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from django.http import Http404
from imager_images.models import Album, Photo


def library_view(request):
    """Library View."""
    user = request.user.get_username()
    if user == '':
        return redirect('home')
    context = {
        'albums': Album.objects.filter(user__username=user),
        'default_cover': settings.STATIC_URL + 'default_cover.thumbnail',
        'photos': Photo.objects.filter(user__username=user)
    }
    return render(request, 'imager_images/library.html', context)


def photo_gallery_view(request):
    """Photo gallery of all a user's photos."""
    context = {'photos': Photo.objects.filter(published='PUBLIC')}
    return render(request, 'imager_images/photo_gallery.html', context)


def album_gallery_view(request):
    """Album gallery of all a user's albums."""
    context = {
        'albums': Album.objects.filter(published='PUBLIC'),
        'default_cover': settings.STATIC_URL + 'default_cover.png',
        'default_cover_thumb': settings.STATIC_URL + 'default_cover.thumbnail',
    }
    return render(request, 'imager_images/album_gallery.html', context)


def photo_detail_view(request, id):
    """Detail view of Photos."""
    photo = get_object_or_404(Photo, id=id)
    if photo.published != 'PUBLIC':
        if photo.user.username != request.user.get_username():
            raise Http404('This Photo does not belong to you')
    context = {
        'photo': photo
    }
    return render(request, 'imager_images/photo_detail.html', context)


def album_detail_view(request, id):
    """Detail view of album."""
    album = get_object_or_404(Album, id=id)
    if album.published != 'PUBLIC':
        if album.user.username != request.user.get_username():
            raise Http404('This album does not belong to you')
    context = {
        'album': album,
        'default_cover': settings.STATIC_URL + 'default_cover.png'
    }
    return render(request, 'imager_images/album_detail.html', context)
