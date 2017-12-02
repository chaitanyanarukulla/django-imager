"""The main views for the Imager site."""
from django.conf import settings
from django.views.generic import TemplateView
from imager_images.models import Photo


class HomeView(TemplateView):
    """Render the home view template."""

    template_name = "imagersite/home.html"

    def get_context_data(self):
        """Get the data to send to the template as context."""
        photos = Photo.objects.filter(published='PUBLIC')
        if photos.count():
            image = photos.order_by('?').first()
            image_url = image.image.url
            image_title = image.title
        else:
            image_url = settings.STATIC_URL + 'test_image.jpg'
            image_title = 'High-Five'
        return {'hero_img_url': image_url,
                'hero_img_title': image_title
                }
