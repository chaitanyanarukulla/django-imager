"""."""
from django.db import models
from django.contrib.auth.models import User
from multiselectfield import MultiSelectField
from django.dispatch import receiver


# Create your models here.
class ImagerProfile(models.Model):
    """Profile for a user of Imager."""

    website = models.URLField(max_length=180, blank=True, null=True)
    location = models.CharField(max_length=180, blank=True, null=True)
    fee = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    camera = models.CharField(max_length=4, blank=True, null=True,
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
    is_active = models.BooleanField(default=True)

    def active():
        """Get a QuerySet of all active profiles."""
        return ImagerProfile.objects.filter(is_active=True)


# @receiver(models.post_save, sender=User)
# def create_profile(sender, **kwargs):
#     """Create a new profile when a User is created."""
#     if kwargs['created']:
#         profile = ImagerProfile(user=kwargs['instance'])
#         profile.save()
