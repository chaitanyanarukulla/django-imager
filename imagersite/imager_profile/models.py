"""Profile for an User."""
from django import forms
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.forms import ModelForm
from multiselectfield import MultiSelectField


class ImagerProfile(models.Model):
    """Profile for a user of Imager."""

    user = models.OneToOneField(User, related_name='profile')

    website = models.URLField(max_length=180, blank=True, null=True)
    location = models.CharField(max_length=180, blank=True, null=True)
    fee = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    camera = models.CharField(max_length=4, blank=True, null=True,
                              choices=(('DSLR', 'Digital Single Lens Reflex'),
                                       ('M', 'Mirrorless'),
                                       ('AC', 'Advanced Compact'),
                                       ('SLR', 'Single Lens Reflex')))
    services = MultiSelectField(
        blank=True, null=True,
        choices=(('weddings', 'Weddings'),
                 ('headshots', 'HeadShots'),
                 ('landscape', 'LandScape'),
                 ('portraits', 'Portraits'),
                 ('art', 'Art')))
    bio = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    photostyles = MultiSelectField(
        blank=True, null=True,
        choices=(('blackandwhite', 'Black and White'),
                 ('night', 'Night'),
                 ('macro', 'Macro'),
                 ('3d', '3D'),
                 ('artistic', 'Artistic'),
                 ('underwater', 'Underwater')))
    is_active = models.BooleanField(default=True)

    def active():
        """Get a QuerySet of all active profiles."""
        return ImagerProfile.objects.filter(is_active=True)

    def __str__(self):
        """The string from of the profile."""
        return 'Profile: ' + self.user.username


@receiver(models.signals.post_save, sender=User)
def create_profile(sender, **kwargs):
    """Create a new profile when a User is created."""
    if kwargs['created']:
        profile = ImagerProfile(user=kwargs['instance'])
        profile.save()


class ImagerProfileForm(ModelForm):
    """Form for an ImagerProfile."""

    email = forms.CharField(max_length=User._meta.get_field('email').max_length,
                            widget=forms.widgets.EmailInput())

    first_name = forms.CharField(max_length=User._meta.get_field('first_name').max_length,
                                 required=False)

    last_name = forms.CharField(max_length=User._meta.get_field('first_name').max_length,
                                required=False)

    class Meta:
        """Meta."""

        model = ImagerProfile
        fields = ['first_name', 'last_name', 'camera', 'bio', 'email',
                  'website', 'phone', 'location', 'fee', 'services',
                  'photostyles']

    def __init__(self, *args, **kwargs):
        """Limit photos to only those by the user."""
        username = kwargs.pop('username')
        super(ImagerProfileForm, self).__init__(*args, **kwargs)
        self.fields['email'].initial = User.objects.get(username=username).email
        self.fields['first_name'].initial = User.objects.get(username=username).first_name
        self.fields['last_name'].initial = User.objects.get(username=username).last_name
