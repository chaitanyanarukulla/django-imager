"""."""
from django.shortcuts import redirect
from django.conf import settings
from django.http import Http404
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView
from imager_images.models import Album, AlbumForm, Photo


class LibraryView(ListView):
    """Library view displays all photo and album views."""

    template_name = 'imager_images/library.html'

    def get(self, *args, **kwargs):
        """Redirect to home if not logged in otherwise display library."""
        if self.request.user.get_username() == '':
            return redirect('home')
        return super(LibraryView, self).get(*args, **kwargs)

    def get_queryset(self, user=None):
        """Get queryset for photos."""
        return Album.objects.filter(user__username=user)

    def get_context_data(self):
        """Get the user's photos and albums."""
        context = super(LibraryView, self).get_context_data()
        user = self.request.user.get_username()
        context['default_cover'] = settings.STATIC_URL + 'default_cover.thumbnail'
        context['albums'] = self.get_queryset(user)
        context['photos'] = Photo.objects.filter(user__username=user)
        return context


class PhotoGalleryView(ListView):
    """Render all public photo as gallery."""

    context_object_name = 'photos'
    template_name = 'imager_images/photo_gallery.html'
    queryset = Photo.objects.filter(published='PUBLIC')


class AlbumGalleryView(ListView):
    """Render all public album as gallery."""

    context_object_name = 'albums'
    template_name = 'imager_images/album_gallery.html'
    queryset = Album.objects.filter(published='PUBLIC')

    def get_context_data(self):
        """Get list of public albums add default cover."""
        context = super(AlbumGalleryView, self).get_context_data()
        context['default_cover'] = settings.STATIC_URL + 'default_cover.png'
        context['default_cover_thumb'] = settings.STATIC_URL + 'default_cover.thumbnail'
        return context


class PhotoDetailView(DetailView):
    """Render the photo detail page."""

    template_name = 'imager_images/photo_detail.html'
    model = Photo
    pk_url_kwarg = 'id'

    def get_object(self):
        """Get the photo object by primary key and check if is public."""
        photo = super(PhotoDetailView, self).get_object()
        if photo.published != 'PUBLIC':
            if photo.user.username != self.request.user.get_username():
                raise Http404('This Photo does not belong to you')
        return photo


class AlbumDetailView(DetailView):
    """Render the Album detail page."""

    template_name = 'imager_images/album_detail.html'
    model = Album
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        """Get context data and add default cover."""
        context = super(AlbumDetailView, self).get_context_data(**kwargs)
        context['default_cover'] = settings.STATIC_URL + 'default_cover.png'
        return context

    def get_object(self):
        """Get the album object by primary key and check if is public."""
        album = super().get_object()
        if album.published != 'PUBLIC':
            if album.user.username != self.request.user.get_username():
                raise Http404('This album does not belong to you')
        return album


class PhotoCreateView(CreateView):
    """Create a new photo and store in the database."""

    template_name = 'imager_images/photo_form.html'
    model = Photo
    fields = ['title', 'description', 'image', 'published']
    success_url = 'library'

    def get(self, *args, **kwargs):
        """Redirect to home if not logged in otherwise display library."""
        if self.request.user.get_username() == '':
            return redirect('home')
        return super(PhotoCreateView, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        """Redirect to home if not logged in otherwise display library."""
        if self.request.user.get_username() == '':
            return redirect('home')
        return super(PhotoCreateView, self).post(*args, **kwargs)

    def form_valid(self, form):
        """Assign user as creater of photo."""
        form.instance.user = self.request.user
        if form.instance.published == 'PUBLIC':
            form.instance.date_published = timezone.now()
        return super(PhotoCreateView, self).form_valid(form)


class AlbumCreateView(CreateView):
    """Create a new album and store in the database."""

    template_name = 'imager_images/album_form.html'
    model = Album
    form_class = AlbumForm
    success_url = 'library'

    def get(self, *args, **kwargs):
        """Redirect to home if not logged in otherwise display library."""
        if self.request.user.get_username() == '':
            return redirect('home')
        return super(AlbumCreateView, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        """Redirect to home if not logged in otherwise display library."""
        if self.request.user.get_username() == '':
            return redirect('home')
        return super(AlbumCreateView, self).post(*args, **kwargs)

    def get_form_kwargs(self):
        """Update the kwargs to include the current user's username."""
        kwargs = super(AlbumCreateView, self).get_form_kwargs()
        kwargs.update({'username': self.request.user.username})
        return kwargs

    def form_valid(self, form):
        """Assign user as creater of album."""
        form.instance.user = self.request.user
        if form.instance.published == 'PUBLIC':
            form.instance.date_published = timezone.now()
        return super(AlbumCreateView, self).form_valid(form)
