"""."""
from django.contrib import admin
from imager_images.models import Photo, Album


admin.site.register((Photo, Album))
