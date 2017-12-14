
"""."""
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import Http404
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from django.urls import reverse_lazy
from imager_images.models import Album, AlbumForm, Photo


class LibraryView(LoginRequiredMixin, ListView):
    """Library view displays all photo and album views."""

    template_name = 'imager_images/library.html'
    login_url = reverse_lazy('login')

    def get_queryset(self, user=None):
        """Get queryset for photos."""
        return Album.objects.filter(user__username=user)

    def get_context_data(self):
        """Get the user's photos and albums."""
        context = super(LibraryView, self).get_context_data()
        user = self.request.user.get_username()
        context['default_cover'] = settings.STATIC_URL + 'default_cover.thumbnail'
        albums = self.get_queryset(user).order_by('date_uploaded')
        photos = Photo.objects.filter(user__username=user).order_by('date_uploaded')

        this_album_page = self.request.GET.get("album_page", 1)
        album_pages = Paginator(albums, 4)

        try:
            albums_page = album_pages.page(this_album_page)
        except PageNotAnInteger:
            albums_page = album_pages.page(1)
        except EmptyPage:
            albums_page = album_pages.page(album_pages.num_pages)
        context['albums'] = albums_page

        this_photo_page = self.request.GET.get("photo_page", 1)
        photo_pages = Paginator(photos, 4)

        try:
            photos_page = photo_pages.page(this_photo_page)
        except PageNotAnInteger:
            photos_page = photo_pages.page(1)
        except EmptyPage:
            photos_page = photo_pages.page(photo_pages.num_pages)
        context['photos'] = photos_page

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

        this_page = self.request.GET.get("page", 1)
        pages = Paginator(self.object.photos.order_by('date_uploaded'), 4)

        try:
            photos_page = pages.page(this_page)
        except PageNotAnInteger:
            photos_page = pages.page(1)
        except EmptyPage:
            photos_page = pages.page(pages.num_pages)

        context['photos_page'] = photos_page

        return context

    def get_object(self):
        """Get the album object by primary key and check if is public."""
        album = super().get_object()
        if album.published != 'PUBLIC':
            if album.user.username != self.request.user.get_username():
                raise Http404('This album does not belong to you')
        return album


class PhotoCreateView(LoginRequiredMixin, CreateView):
    """Create a new photo and store in the database."""

    template_name = 'imager_images/photo_create.html'
    login_url = reverse_lazy('login')
    model = Photo
    fields = ['title', 'description', 'image', 'published']
    success_url = reverse_lazy('library')

    def form_valid(self, form):
        """Assign user as creater of photo."""
        form.instance.user = self.request.user
        return super(PhotoCreateView, self).form_valid(form)


class AlbumCreateView(LoginRequiredMixin, CreateView):
    """Create a new album and store in the database."""

    template_name = 'imager_images/album_create.html'
    login_url = reverse_lazy('login')
    model = Album
    form_class = AlbumForm
    success_url = reverse_lazy('library')

    def get_form_kwargs(self):
        """Update the kwargs to include the current user's username."""
        kwargs = super(AlbumCreateView, self).get_form_kwargs()
        kwargs.update({'username': self.request.user.username})
        return kwargs

    def form_valid(self, form):
        """Assign user as creater of album."""
        form.instance.user = self.request.user
        return super(AlbumCreateView, self).form_valid(form)


class AlbumEditView(LoginRequiredMixin, UpdateView):
    """Update a existing album in the db."""

    template_name = 'imager_images/album_edit.html'
    login_url = reverse_lazy('login')
    pk_url_kwarg = 'id'
    model = Album
    form_class = AlbumForm
    success_url = reverse_lazy('library')

    def get_queryset(self):
        """Limit editable albums to those owned by the user."""
        return Album.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        """Update the kwargs to include the current user's username."""
        kwargs = super(AlbumEditView, self).get_form_kwargs()
        kwargs.update({'username': self.request.user.username})
        return kwargs


class PhotoEditView(LoginRequiredMixin, UpdateView):
    """Edit a new photo and store in the database."""

    template_name = 'imager_images/photo_edit.html'
    login_url = reverse_lazy('login')
    pk_url_kwarg = 'id'
    model = Photo
    fields = ['title', 'description', 'image', 'published']
    success_url = reverse_lazy('library')

    def get_queryset(self):
        """Limit editable photos to those owned by the user."""
        return Photo.objects.filter(user=self.request.user)
