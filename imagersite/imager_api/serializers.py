from rest_framework import serializers
from imager_images.models import Photo


class PhotoSerializer(serializers.ModelSerializer):
    """Serializer for listing photo objects."""

    class Meta:
        model = Photo
        fields = ('id', 'image', 'title', 'description', 'date_uploaded',
                  'date_modified', 'date_published', 'published')
