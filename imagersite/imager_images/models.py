"""Photo and Album models created by a User."""
from django.db import models
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.dispatch import receiver
from django.utils import timezone
from sorl.thumbnail import ImageField


class Photo(models.Model):
    """Photo uploaded by a User."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = ImageField(upload_to='images')
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
        return self.title


@receiver(models.signals.post_save, sender=Photo)
def set_photo_published_date(sender, instance, **kwargs):
    """Update the date published if published."""
    if instance.published == 'PUBLIC' and not instance.date_published:
        instance.date_published = timezone.now()
        instance.save()


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
        return self.title


@receiver(models.signals.post_save, sender=Album)
def set_album_published_date(sender, instance, **kwargs):
    """Update the date published if published."""
    if instance.published == 'PUBLIC' and not instance.date_published:
        instance.date_published = timezone.now()
        instance.save()


class AlbumForm(ModelForm):
    """Form for an Album."""

    class Meta:
        """Meta."""

        model = Album
        fields = ['title', 'description', 'photos', 'cover', 'published']

    def __init__(self, *args, **kwargs):
        """Limit photos to only those by the user."""
        username = kwargs.pop('username')
        super(AlbumForm, self).__init__(*args, **kwargs)
        self.fields['photos'].queryset = Photo.objects.filter(user__username=username)
        self.fields['cover'].queryset = Photo.objects.filter(user__username=username)
