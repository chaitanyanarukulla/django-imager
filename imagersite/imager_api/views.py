from imager_images.models import Photo
from imager_api.serializers import PhotoSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated


class PhotoList(generics.ListAPIView):
    """List all of a user's photos."""

    permission_classes = (IsAuthenticated,)

    serializer_class = PhotoSerializer

    def get_queryset(self):
        """Limit listed photos to those owned by the user."""
        return Photo.objects.filter(user=self.request.user)
