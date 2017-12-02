"""The main views for the Imager site."""
from django.conf import settings
from django.shortcuts import render
from imager_images.models import Photo


def home_view(request):
    """Get the Home page."""
    if Photo.objects.filter(published='PUBLIC').count():
        image = Photo.objects.filter(published='PUBLIC').order_by('?').first()
        image_url = image.image.url
        image_title = image.title
    else:
        image_url = settings.STATIC_URL + 'test_image.jpg'
        image_title = 'High-Five'

    return render(
        request,
        'imagersite/home.html',
        {
            'hero_img_url': image_url,
            'hero_img_title': image_title
        }
    )
