"""."""
from django.db import models
from django.contrib.auth.models import User
from multiselectfield import MultiSelectField


# Create your models here.
class ImagerProfile(models.Model):
    """Profile for a user of Imager."""

    website = models.URLField(max_length=180, blank=True, null=True)
    location = models.CharField(max_length=180, blank=True, null=True)
    fee = models.FloatField(blank=True, null=True)
    camera = models.CharField(max_length=180, blank=True, null=True,
                              choices=(('DSLR', 'Digital Single Lens Reflex'),
                                       ('M', 'Mirrorless'),
                                       ('AC', 'Advanced Compact'),
                                       ('SLR', 'Single Lens Reflex')))
    services = MultiSelectField(
        choices=(('weddings', 'Weddings'),
                 ('headshots', 'HeadShots'),
                 ('landscape', 'LandScape'),
                 ('portraits', 'Portraits'),
                 ('art', 'Art')))
    bio = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    photostyles = MultiSelectField(
        choices=(('blackandwhite', 'Black and White'),
                 ('night', 'Night'),
                 ('macro', 'Macro'),
                 ('3d', '3D'),
                 ('artistic', 'Artistic'),
                 ('underwater', 'Underwater')))
    user = models.OneToOneField(User, related_name='profile')

    @property
    def is_active(self):
        """Whether the user is currently active or not."""
        return self.user.is_active

    def active():
        """Get a QuerySet of all active profiles."""
        return User.objects.filter(is_active=True)
