from django.contrib import admin
from imager_images.models import Photo, Album
# Register your models here.


admin.site.register((Photo, Album))