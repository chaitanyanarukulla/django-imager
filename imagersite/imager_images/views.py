"""."""
from django.shortcuts import render, redirect
from django.conf import settings
from imager_images.models import Album, Photo


def library_view(request):
    """Library View."""
    user = request.user.get_username()
    if user == '':
        return redirect('home')

    photos = Photo.objects.filter(user__username=user)

    albums = Album.objects.filter(user__username=user)

    context = {
        'albums': albums,
        'default_cover': settings.STATIC_URL + 'default_cover.thumbnail',
        'photos': photos
    }
    return render(request, 'imager_images/library.html', context)


def photo_gallery_view(request):
    """Photo gallery of all a user's photos."""
    user = request.user.get_username()
    if user == '':
        return redirect('home')

    context = {'photos': Photo.objects.filter(user__username=user)}
    return render(request, 'imager_images/photo_gallery.html', context)
