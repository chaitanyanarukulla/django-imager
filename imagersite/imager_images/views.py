"""."""
from django.shortcuts import render, redirect
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
        im = Image.open(photo.image.path)
        im.thumbnail((250, 250))
        im.save(file + ".thumbnail", "JPEG")
        photo_data = {}
        photo_data['image'] = photo.image.path
        photo_data['thumbnail'] = file + ".thumbnail"
        photo_data['title'] = photo.title
        photos_data.append(photo_data)
    albums = Album.objects.filter(user__username=user)
    albums_data = []
    for album in albums:
        file, exe = os.path.splitext(album.cover.image.path)
        im = Image.open(album.cover.image.path)
        im.thumbnail((250, 250))
        im.save(file + ".thumbnail", "JPEG")
        album_data = {}
        album_data['thumbnail'] = file + ".thumbnail"
        album_data['title'] = album.title
        albums_data.append(album_data)

    context = {
        'albums': albums_data,
        'photos': photos_data
    }
    return render(request, 'imager_images/library.html', context)
