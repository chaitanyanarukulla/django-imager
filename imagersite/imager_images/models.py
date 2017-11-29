"""Photo and Album models created by a User."""
from django.db import models
from django.contrib.auth.models import User


class Photo(models.Model):
    """Photo uploaded by a User."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images')
    title = models.CharField(max_length=180, blank=True, default='Untitled')
    description = models.TextField(blank=True, null=True)
    date_uploaded = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    date_published = models.DateTimeField(blank=True, null=True)
    published = models.CharField(
        max_length=7,
        choices=(('PRIVATE', 'Private'),
                 ('SHARED', 'Shared'),
                 ('PUBLIC', 'Public'))
    )

    def __str__(self):
        """The string from of the image."""
        return 'Photo: ' + self.title


class Album(models.Model):
    """Album of Photos created by the User."""

    # objects = models.ModelManager()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    photos = models.ManyToManyField(Photo, related_name='albums')
    title = models.CharField(max_length=180, blank=True, default='Untitled')
    cover = models.ForeignKey(Photo, blank=True, null=True, related_name='+')
    description = models.TextField(blank=True, null=True)
    date_uploaded = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    date_published = models.DateTimeField(blank=True, null=True)
    published = models.CharField(
        max_length=7,
        choices=(('PRIVATE', 'Private'),
                 ('SHARED', 'Shared'),
                 ('PUBLIC', 'Public'))
    )

    def __str__(self):
        """The string from of the album."""
        return 'Album: ' + self.title
