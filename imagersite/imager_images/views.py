"""."""
from django.shortcuts import render, redirect
from django.conf import settings
from imager_images.models import Album, Photo
from PIL import Image
import os


def library_view(request):
    """Library View."""
    user = request.user.get_username()
    if user == '':
        return redirect('home')
    photos = Photo.objects.filter(user__username=user)
    photos_data = []
    for photo in photos:
        file, exe = os.path.splitext(photo.image.path)
        if not os.path.isfile(file + ".thumbnail"):
            im = Image.open(photo.image.path)
            size = min(im.size)
            im = im.crop((0, 0, size, size))
            im.thumbnail((250, 250))
            im.save(file + ".thumbnail", "JPEG")
        photo_data = {}
        url, exe = os.path.splitext(photo.image.url)
        photo_data['image'] = photo.image.url
        photo_data['thumbnail'] = url + ".thumbnail"
        photo_data['title'] = photo.title
        photos_data.append(photo_data)
    albums = Album.objects.filter(user__username=user)
    albums_data = []
    for album in albums:
        album_data = {}
        if not album.cover:
            album_data['thumbnail'] = settings.STATIC_URL + 'default_cover.thumbnail'
        else:
            file, exe = os.path.splitext(album.cover.image.path)
            if not os.path.isfile(file + ".thumbnail"):
                im = Image.open(album.cover.image.path)
                size = min(im.size)
                im = im.crop((0, 0, size, size))
                im.thumbnail((250, 250))
                im.save(file + ".thumbnail", "JPEG")
            url, exe = os.path.splitext(album.cover.image.url)
            album_data['thumbnail'] = url + ".thumbnail"
        album_data['title'] = album.title
        albums_data.append(album_data)

    context = {
        'albums': albums_data,
        'photos': photos_data
    }
    return render(request, 'imager_images/library.html', context)
