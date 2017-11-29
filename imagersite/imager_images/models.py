"""."""
from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Photo(models.Model):
    """."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images')
    title = models.CharField(max_length=180, blank=True, null=True)
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


class Album(models.Model):
    """."""

    # objects = models.ModelManager()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    photos = models.ManyToManyField(Photo, related_name='albums')
    title = models.CharField(max_length=180)
    cover = models.ForeignKey(Photo, blank=True, null=True)
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
