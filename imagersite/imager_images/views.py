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
    for photo in photos:
        file, exe = os.path.splitext(photo.image.path)
        im = Image.open(photo.image.path)
        im.thumbnail((250, 200))
        im.save(file + ".thumbnail", "JPEG")
    context = {
        'albums': [{}],
        'photos': [{}]
    }
    return render(request, 'imager_images/library.html', context)
