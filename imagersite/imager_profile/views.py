"""View functions for the profile page."""
from django.shortcuts import redirect
from django.views.generic import DetailView
from imager_profile.models import ImagerProfile
from imager_images.models import Album, Photo


class ProfileView(DetailView):
    """Profile view for a single user."""

    template_name = 'imager_profile/profile.html'
    model = ImagerProfile
    slug_field = 'user__username'
    slug_url_kwarg = 'username'

    def get(self, *args, **kwargs):
        """Redirect home if not logged in."""
        # import pdb; pdb.set_trace()
        if not self.kwargs['username']:
            self.kwargs['username'] = self.request.user.get_username()
            if self.kwargs['username'] == '':
                return redirect('home')

        if self.kwargs['username'].endswith('/'):
            self.kwargs['username'] = self.kwargs['username'][:-1]
        return super(ProfileView, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        """Get the user's profile, photos, and albums."""
        # import pdb; pdb.set_trace()
        context = super(ProfileView, self).get_context_data(**kwargs)
        username = kwargs['object'].user.username

        owner = False
        if username == self.request.user.username:
            owner = True

        context['owner'] = owner

        photos = Photo.objects.filter(user__username=username)
        albums = Album.objects.filter(user__username=username)

        if not owner:
            photos = photos.filter(published='PUBLIC')
            albums = albums.filter(published='PUBLIC')

        context['albums'] = albums
        context['album_private_count'] = albums.filter(published='PRIVATE').count()
        context['album_public_count'] = albums.filter(published='PUBLIC').count()

        context['photos'] = photos
        context['photo_private_count'] = photos.filter(published='PRIVATE').count()
        context['photo_public_count'] = photos.filter(published='PUBLIC').count()

        return context
