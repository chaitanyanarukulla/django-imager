"""View functions for the profile page."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import DetailView, UpdateView
from django.urls import reverse_lazy
from imager_profile.models import ImagerProfile, ImagerProfileForm
from imager_images.models import Album, Photo


class ProfileView(DetailView):
    """Profile view for a single user."""

    template_name = 'imager_profile/profile.html'
    model = ImagerProfile
    slug_field = 'user__username'
    slug_url_kwarg = 'username'

    def get(self, *args, **kwargs):
        """Redirect home if not logged in."""
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


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Edit a new photo and store in the database."""

    template_name = 'imager_profile/profile_edit.html'
    model = ImagerProfile
    slug_field = 'user__username'
    slug_url_kwarg = 'username'
    form_class = ImagerProfileForm
    success_url = '/profile/'
    login_url = reverse_lazy('login')

    def get_form_kwargs(self):
        """Update the kwargs to include the current user's username."""
        kwargs = super(ProfileEditView, self).get_form_kwargs()
        kwargs.update({'username': self.request.user.username})
        return kwargs

    def get(self, *args, **kwargs):
        """Redirect to home if not logged in otherwise display library."""
        self.kwargs['username'] = self.request.user.get_username()
        return super(ProfileEditView, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        """Redirect to home if not logged in otherwise display library."""
        self.kwargs['username'] = self.request.user.get_username()
        return super(ProfileEditView, self).post(*args, **kwargs)

    def form_valid(self, form):
        """Assign user as Edit of profile."""
        form.instance.user.email = form.data['email']
        form.instance.user.first_name = form.data['first_name']
        form.instance.user.last_name = form.data['last_name']
        form.instance.user.save()
        return super(ProfileEditView, self).form_valid(form)
