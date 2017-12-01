"""."""
from django.shortcuts import render, redirect
from django.conf import settings
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
    user = request.user.get_username()
    if user == '':
        return redirect('home')

    context = {'photos': Photo.objects.filter(user__username=user)}
    return render(request, 'imager_images/photo_gallery.html', context)


def album_gallery_view(request):
    """Album gallery of all a user's albums."""
    user = request.user.get_username()
    if user == '':
        return redirect('home')

    context = {
        'albums': Album.objects.filter(user__username=user),
        'default_cover': settings.STATIC_URL + 'default_cover.png',
        'default_cover_thumb': settings.STATIC_URL + 'default_cover.thumbnail',
    }
    return render(request, 'imager_images/album_gallery.html', context)
