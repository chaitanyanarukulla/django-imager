"""Tests for the Photo and Album models."""
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms.models import modelform_factory
from django.http import Http404
from django.test import override_settings, RequestFactory, TestCase
from django.urls import reverse_lazy
from imager_images.models import Photo, Album, AlbumForm
from imager_profile.tests import UserFactory
from datetime import datetime
import factory
import os


class PhotoFactory(factory.django.DjangoModelFactory):
    """Factory for fake Photo."""

    class Meta:
        """Meta."""

        model = Photo

    image = SimpleUploadedFile(
        name='sample_img.jpg',
        content=open(
            os.path.join(settings.BASE_DIR, 'static/test_image.jpg'), 'rb'
        ).read(),
        content_type="image/jpeg"
    )
    title = factory.Faker('word')
    description = factory.Faker('sentence')
    published = 'PUBLIC'


class AlbumFactory(factory.django.DjangoModelFactory):
    """Factory for fake Album."""

    class Meta:
        """Meta."""

        model = Album

    title = factory.Faker('word')
    description = factory.Faker('sentence')
    published = 'PUBLIC'


class PhotoAlbumTests(TestCase):
    """Tests for the imager_profile module."""

    @classmethod
    @override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR,
                                               "test_media_for_photos"))
    def setUpClass(cls):
        """Add one minimal user to the database."""
        super(PhotoAlbumTests, cls).setUpClass()

        os.system('mkdir {}'.format(
            os.path.join(settings.BASE_DIR, 'test_media_for_photos')
        ))

        user = UserFactory()
        user.set_password(factory.Faker('password'))
        user.save()
        cls.user = user

        photo = PhotoFactory(title='wedding', description='lovely wedding',
                             published='PRIVATE', user=user)
        photo.save()

        album1 = AlbumFactory(title='first', description='this is first',
                              published='PRIVATE', user=user)
        album1.save()

        for _ in range(10):
            photo = PhotoFactory(user=user)
            photo.save()
            album1.photos.add(photo)

        album2 = AlbumFactory(title='second', user=user)
        album2.save()

        for _ in range(20):
            photo = PhotoFactory(user=user)
            photo.save()
            album2.photos.add(photo)

        for _ in range(5):
            photo = PhotoFactory(user=user)
            photo.save()
            album1.photos.add(photo)
            album2.photos.add(photo)

        user = UserFactory()
        user.set_password(factory.Faker('password'))
        user.save()
        photo = PhotoFactory(title='sport', user=user)
        photo.save()

        album1 = AlbumFactory(title='sports', user=user)
        album1.save()

    @classmethod
    def tearDownClass(cls):
        """Remove the test directory."""
        super(PhotoAlbumTests, cls).tearDownClass()
        os.system('rm -rf {}'.format(
            os.path.join(settings.BASE_DIR, 'test_media_for_photos')
        ))

    def test_photo_to_string_is_correct(self):
        """Test that the __str__ method returns the photo title."""
        one_photo = Photo.objects.get(title='wedding')
        self.assertEqual(str(one_photo), 'wedding')

    def test_album_to_string_is_correct(self):
        """Test that the __str__ method returns the album title."""
        one_album = Album.objects.get(title='first')
        self.assertEqual(str(one_album), 'first')

    def test_all_photos_are_added_to_the_database(self):
        """Test that all created photos are added to the database."""
        self.assertEqual(Photo.objects.count(), 37)

    @override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR,
                                               "test_media_for_photos"))
    def test_all_photos_are_added_to_the_media_directory(self):
        """Test that all created photos are added to the media directory."""
        path = os.path.join(settings.MEDIA_ROOT, 'images')
        files = [name for name in os.listdir(path) if name.endswith('.jpg')]
        self.assertEqual(len(files), 37)

    def test_photos_are_added_to_an_album(self):
        """Test that all created photos are added to the database."""
        photos = Photo.objects.filter(albums__title='first').count()
        self.assertEqual(photos, 15)

    def test_photo_has_user(self):
        """Test that the photo has a user."""
        one_photo = Photo.objects.get(title='wedding')
        self.assertEqual(one_photo.user, self.user)

    def test_photo_has_description(self):
        """Test that the photo has a description."""
        one_photo = Photo.objects.get(title='wedding')
        self.assertEqual(one_photo.description, 'lovely wedding')

    def test_photo_has_published(self):
        """Test that the photo has a published."""
        one_photo = Photo.objects.get(title='wedding')
        self.assertEqual(one_photo.published, 'PRIVATE')

    def test_photo_has_date_uploaded(self):
        """Test that the photo has a date-uploaded that is now by default."""
        one_photo = Photo.objects.get(title='wedding')
        now = datetime.now().strftime('%x %X')[:2]
        self.assertEqual(one_photo.date_uploaded.strftime('%x %X')[:2], now)

    def test_photo_has_date_modified(self):
        """Test that the photo has a date-modified that is now by default."""
        one_photo = Photo.objects.get(title='wedding')
        now = datetime.now().strftime('%x %X')[:2]
        self.assertEqual(one_photo.date_modified.strftime('%x %X')[:2], now)

    @override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR,
                                               "test_media_for_photos"))
    def test_photo_modified_changes_modified_date_not_uploaded_date(self):
        """Test the uploaded date does not change when a photo is modified."""
        user = UserFactory()
        user.set_password(factory.Faker('password'))
        user.save()
        photo = PhotoFactory(user=user)
        photo.save()
        created_upload_date = photo.date_uploaded
        created_modify_date = photo.date_modified
        photo.title = 'fun'
        photo.save()
        self.assertEqual(photo.date_uploaded, created_upload_date)
        self.assertNotEqual(photo.date_modified, created_modify_date)

    def test_private_photo_has_no_date_published(self):
        """Test that private photo has  date-published that is None."""
        one_photo = Photo.objects.get(title='wedding')
        self.assertIsNone(one_photo.date_published)

    def test_public_photo_has_date_published(self):
        """Test that public photo has a date-published."""
        one_photo = Photo.objects.filter(albums__title='second').first()
        now = datetime.now().strftime('%x %X')[:2]
        self.assertEqual(one_photo.date_published.strftime('%x %X')[:2], now)

    def test_all_albums_are_added_to_the_database(self):
        """Test that all created albums are added to the database."""
        self.assertEqual(Album.objects.count(), 3)

    def test_album_has_user(self):
        """Test that the album has a user."""
        one_album = Album.objects.get(title='first')
        self.assertEqual(one_album.user, self.user)

    def test_album_has_description(self):
        """Test that the album has a description."""
        one_album = Album.objects.get(title='first')
        self.assertEqual(one_album.description, 'this is first')

    def test_album_has_published(self):
        """Test that the album has a published."""
        one_album = Album.objects.get(title='first')
        self.assertEqual(one_album.published, 'PRIVATE')

    def test_album_has_date_uploaded(self):
        """Test that the album has a date-uploaded that is now by default."""
        one_album = Album.objects.get(title='first')
        now = datetime.now().strftime('%x %X')[:2]
        self.assertEqual(one_album.date_uploaded.strftime('%x %X')[:2], now)

    def test_album_has_date_modified(self):
        """Test that the album has a date-modified that is now by default."""
        one_album = Album.objects.get(title='first')
        now = datetime.now().strftime('%x %X')[:2]
        self.assertEqual(one_album.date_modified.strftime('%x %X')[:2], now)

    @override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR,
                                               "test_media_for_photos"))
    def test_album_modified_changes_modified_date_not_uploaded_date(self):
        """Test the uploaded date does not change when a album is modified."""
        user = UserFactory()
        user.set_password(factory.Faker('password'))
        user.save()
        album = AlbumFactory(user=user)
        album.save()
        created_upload_date = album.date_uploaded
        created_modify_date = album.date_modified
        album.title = 'fun'
        album.save()
        self.assertEqual(album.date_uploaded, created_upload_date)
        self.assertNotEqual(album.date_modified, created_modify_date)

    def test_private_album_has_no_date_published(self):
        """Test that private album has a date-published that is None."""
        one_album = Album.objects.get(title='first')
        self.assertIsNone(one_album.date_published)

    def test_public_album_has_date_published(self):
        """Test that public album has a date-published."""
        one_album = Album.objects.get(title='second')
        now = datetime.now().strftime('%x %X')[:2]
        self.assertEqual(one_album.date_published.strftime('%x %X')[:2], now)

    def test_album_form_photos_are_limited_to_current_users(self):
        """Test album form photos are limited to current users."""
        form = AlbumForm(username=self.user.username)
        self.assertEqual(form.fields['photos'].queryset.count(), 36)


"""Unit tests for the Photo and Album view classes."""


class PhotoAlbumViewTests(TestCase):
    """Tests for the views of imager_images."""

    @classmethod
    @override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR,
                                               "test_media_for_photo_view"))
    def setUpClass(cls):
        """Add one user to the database."""
        super(PhotoAlbumViewTests, cls).setUpClass()

        os.system('mkdir {}'.format(
            os.path.join(settings.BASE_DIR, 'test_media_for_photo_view')
        ))

        cls.request = RequestFactory()

        user = UserFactory(username='bob')
        user.set_password(factory.Faker('password'))
        user.save()
        cls.bob = user

        album = AlbumFactory(title='bob first', description='this is first',
                             published='PRIVATE', user=user)
        album.save()

        for _ in range(5):
            photo = PhotoFactory(user=user, published='PRIVATE')
            photo.save()
            album.photos.add(photo)

        album = AlbumFactory(title='bob second', description='this is second',
                             published='PUBLIC', user=user)
        album.save()

        for _ in range(10):
            photo = PhotoFactory(user=user)
            photo.save()
            album.photos.add(photo)

        user = UserFactory(username='rob')
        user.set_password(factory.Faker('password'))
        user.save()

        album = AlbumFactory(title='rob first', description='this is first',
                             published='PRIVATE', user=user)
        album.save()

        for _ in range(3):
            photo = PhotoFactory(user=user, published='PRIVATE')
            photo.save()
            album.photos.add(photo)

        album = AlbumFactory(title='rob second', description='this is second',
                             published='PUBLIC', user=user)
        album.save()

        for _ in range(13):
            photo = PhotoFactory(user=user)
            photo.save()
            album.photos.add(photo)

    @classmethod
    def tearDownClass(cls):
        """Remove the test directory."""
        super(PhotoAlbumViewTests, cls).tearDownClass()
        os.system('rm -rf {}'.format(
            os.path.join(settings.BASE_DIR, 'test_media_for_photo_view')))

    def test_library_view_logged_in_displays_all_photos_and_albums(self):
        """Test that library_view displays all logged in user's things."""
        from imager_images.views import LibraryView
        request = self.request.get('')
        request.user = self.bob
        view = LibraryView(request=request)
        response = view.get(request)
        response.render()
        image_count = response.content.count(b'<img')
        self.assertEqual(image_count, 17)

    def test_library_view_get_queryset_list_all_users_albums(self):
        """Test library view get queryset list all users albums."""
        from imager_images.views import LibraryView
        view = LibraryView()
        albums = view.get_queryset(self.bob)
        self.assertEqual(albums.count(), 2)

    def test_library_view_logged_in_context_has_all_photos_and_albums(self):
        """Test libraryview returns context data with all logged in user's photos and albums."""
        from imager_images.views import LibraryView
        request = self.request.get('')
        request.user = self.bob
        view = LibraryView(request=request, object_list='')
        data = view.get_context_data()
        self.assertEqual(data['albums'].count(), 2)
        self.assertEqual(data['photos'].count(), 15)
        self.assertIn('default_cover', data)

    def test_album_gallery_view_has_all_public_albums(self):
        """Test that the album_gallery_view has all public albums."""
        from imager_images.views import AlbumGalleryView
        view = AlbumGalleryView(object_list='')
        data = view.get_context_data()
        self.assertIn('albums', data)
        self.assertIn('default_cover', data)

    def test_photo_detail_view_non_public_photo_raises_404(self):
        """Test that a non public photo for photo_detail_view raises a 404."""
        from imager_images.views import PhotoDetailView
        photo = Photo.objects.filter(published='PRIVATE').first()
        request = self.request.get('')
        request.user = AnonymousUser()
        view = PhotoDetailView(request=request, kwargs={'id': photo.id})
        with self.assertRaises(Http404):
            view.get_object()

    def test_photo_detail_view_valid_id_gets_correct_photo(self):
        """Test that photo_detail_view for valid id has correct photo."""
        from imager_images.views import PhotoDetailView
        photo = Photo.objects.filter(published='PUBLIC').first()
        request = self.request.get('')
        request.user = AnonymousUser()
        view = PhotoDetailView(request=request, kwargs={'id': photo.id})
        response = view.get_object()
        self.assertEqual(response.image, photo.image)

    def test_album_detail_view_non_public_album_raises_404(self):
        """Test that a non public album for album_detail_view raises a 404."""
        from imager_images.views import AlbumDetailView
        album = Album.objects.filter(published='PRIVATE').first()
        request = self.request.get('')
        request.user = AnonymousUser()
        view = AlbumDetailView(request=request, kwargs={'id': album.id})
        with self.assertRaises(Http404):
            view.get_object()

    def test_album_detail_view_valid_id_gets_correct_album(self):
        """Test that album_detail_view for valid id has correct album."""
        from imager_images.views import AlbumDetailView
        album = Album.objects.filter(published='PUBLIC').first()
        request = self.request.get('')
        request.user = AnonymousUser()
        view = AlbumDetailView(request=request, kwargs={'id': album.id})
        response = view.get_object()
        self.assertEqual(response.photos, album.photos)

    def test_album_detail_view_has_album(self):
        """Test that the album detail_view has album."""
        from imager_images.views import AlbumDetailView
        view = AlbumDetailView(object='')
        data = view.get_context_data()
        self.assertIn('view', data)
        self.assertIn('default_cover', data)

    def test_photo_create_view_logged_in_has_upload_form(self):
        """Test that photo create view  has upload form."""
        from imager_images.views import PhotoCreateView
        request = self.request.get('')
        request.user = self.bob
        view = PhotoCreateView(request=request)
        response = view.get(request)
        response.render()
        self.assertIn(b'Upload New Photo', response.content)

    @override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR,
                                               "test_media_for_photo_view"))
    def test_photo_create_view_post_logged_in_create_new_photo(self):
        """Test that photo create view post login creates new photo."""
        from imager_images.views import PhotoCreateView
        request = self.request.post('')
        request.user = self.bob
        request.POST = {'title': 'test', 'description': 'testing', 'published': 'PRIVATE'}
        image = SimpleUploadedFile(
            name='sample_img.jpg',
            content=open(
                os.path.join(settings.BASE_DIR, 'static/test_image.jpg'), 'rb'
            ).read(),
            content_type="image/jpeg"
        )
        request._files = {'image': image}
        view = PhotoCreateView(request=request)
        view.post(request)
        photo = Photo.objects.get(title='test')
        self.assertIsNotNone(photo)
        self.assertEqual(photo.description, 'testing')

    @override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR,
                                               "test_media_for_photo_view"))
    def test_photo_create_view_form_valid_sets_current_user_as_user(self):
        """Test photo create view form valid sets current user as user."""
        from imager_images.views import PhotoCreateView
        form_class = modelform_factory(Photo, fields=['title', 'description',
                                                      'image', 'published'])
        request = self.request.post('')
        request.user = self.bob
        view = PhotoCreateView(request=request)
        image = SimpleUploadedFile(
            name='sample_img.jpg',
            content=open(
                os.path.join(settings.BASE_DIR, 'static/test_image.jpg'), 'rb'
            ).read(),
            content_type="image/jpeg"
        )
        files = {'image': image}
        data = {'title': 'test2', 'description': 'testing2', 'published': 'PRIVATE'}
        form = form_class(data=data, files=files)
        form.is_valid()
        view.form_valid(form)
        self.assertIs(self.bob, form.instance.user)

    def test_album_create_view_logged_in_has_upload_form(self):
        """Test that album create view  has upload form."""
        from imager_images.views import AlbumCreateView
        request = self.request.get('')
        request.user = self.bob
        view = AlbumCreateView(request=request)
        response = view.get(request)
        response.render()
        self.assertIn(b'Create New Album', response.content)

    def test_album_create_view_post_logged_in_create_new_album(self):
        """Test that album create view post login creates new album."""
        from imager_images.views import AlbumCreateView
        request = self.request.post('')
        request.user = self.bob
        request.POST = {'title': 'test', 'description': 'testing',
                        'photos': ['83'], 'published': 'PRIVATE', 'cover': ''}
        view = AlbumCreateView(request=request)
        view.post(request)
        album = Album.objects.get(title='test')
        self.assertIsNotNone(album)
        self.assertEqual(album.description, 'testing')

    def test_album_create_view_form_valid_sets_current_user_as_user(self):
        """Test album create view form valid sets current user as user."""
        from imager_images.views import AlbumCreateView
        form_class = AlbumForm
        request = self.request.post('')
        request.user = self.bob
        view = AlbumCreateView(request=request)
        data = {'title': 'test', 'description': 'testing',
                         'photos': ['86'], 'published': 'PRIVATE', 'cover': ''}
        form = form_class(data=data, username=request.user.username)
        form.is_valid()
        view.form_valid(form)
        self.assertIs(self.bob, form.instance.user)

    def test_album_create_view_get_form_kwargs_assigns_current_user(self):
        """Test album create view get form kwargs assigns current user."""
        from imager_images.views import AlbumCreateView
        request = self.request.get('')
        request.user = self.bob
        view = AlbumCreateView(request=request)
        kwargs = view.get_form_kwargs()
        self.assertIn('username', kwargs)
        self.assertEqual(kwargs['username'], 'bob')

    def test_album_edit_view_get_form_kwargs_assigns_current_user(self):
        """Test album edit view get form kwargs assigns current user."""
        from imager_images.views import AlbumEditView
        request = self.request.get('')
        request.user = self.bob
        view = AlbumEditView(request=request)
        kwargs = view.get_form_kwargs()
        self.assertIn('username', kwargs)
        self.assertEqual(kwargs['username'], 'bob')


"""Tests for the Photo and Album routes."""


class PhotoAlbumRouteTests(TestCase):
    """Tests for the routes of imager_images."""

    @classmethod
    @override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR,
                                               "test_media_for_photo_route"))
    def setUpClass(cls):
        """Add one minimal user to the database."""
        super(PhotoAlbumRouteTests, cls).setUpClass()

        os.system('mkdir {}'.format(
            os.path.join(settings.BASE_DIR, 'test_media_for_photo_route')
        ))

        user = UserFactory(username='bob')
        user.set_password('password')
        user.save()
        cls.bob = user

        album = AlbumFactory(title='bob first', description='this is first',
                             published='PRIVATE', user=user)
        album.save()

        for _ in range(5):
            photo = PhotoFactory(user=user, published='PRIVATE')
            photo.save()
            album.photos.add(photo)

        album = AlbumFactory(title='bob second', description='this is second',
                             published='PUBLIC', user=user)
        album.save()

        for _ in range(10):
            photo = PhotoFactory(user=user)
            photo.save()
            album.photos.add(photo)

        user = UserFactory(username='rob')
        user.set_password(factory.Faker('password'))
        user.save()

        album = AlbumFactory(title='rob first', description='this is first',
                             published='PRIVATE', user=user)
        album.save()

        for _ in range(3):
            photo = PhotoFactory(user=user, published='PRIVATE')
            photo.save()
            album.photos.add(photo)

        album = AlbumFactory(title='rob second', description='this is second',
                             published='PUBLIC', user=user)
        album.save()

        for _ in range(13):
            photo = PhotoFactory(user=user)
            photo.save()
            album.photos.add(photo)

    @classmethod
    def tearDownClass(cls):
        """Remove the test directory."""
        super(PhotoAlbumRouteTests, cls).tearDownClass()
        os.system('rm -rf {}'.format(
            os.path.join(settings.BASE_DIR, 'test_media_for_photo_route')))

    def test_library_route_not_logged_in_gets_302(self):
        """Test that library route gets 302 status code if not logged in."""
        response = self.client.get(reverse_lazy('library'))
        self.assertEqual(response.status_code, 302)

    def test_library_route_redirects_login_not_logged_in(self):
        """Test that library route redirects login if not logged in."""
        response = self.client.get(reverse_lazy('library'), follow=True)
        self.assertIn(b'Login</h1>', response.content)

    def test_library_route_logged_in_displays_all_photos_and_albums(self):
        """Test that library route displays all logged in user's things."""
        self.client.login(username='bob', password='password')
        response = self.client.get(reverse_lazy('library'))
        image_count = response.content.count(b'<img')
        db_photo_count = Photo.objects.filter(user=self.bob).count()
        db_album_count = Album.objects.filter(user=self.bob).count()
        self.assertEqual(image_count, db_photo_count + db_album_count)

    def test_photo_gallery_route_has_all_public_photos(self):
        """Test that the photo gallery route has all public photos."""
        response = self.client.get(reverse_lazy('photo_gallery'))
        image_count = response.content.count(b'<img')
        db_count = Photo.objects.filter(published='PUBLIC').count()
        self.assertEqual(image_count, db_count)

    def test_album_gallery_route_has_all_public_albums(self):
        """Test that the album gallery route has all public albums."""
        response = self.client.get(reverse_lazy('album_gallery'))
        image_count = response.content.count(b'<img')
        db_count = Album.objects.filter(published='PUBLIC').count()
        self.assertEqual(image_count, db_count)

    def test_photo_detail_route_invalid_id_raises_404(self):
        """Test that an invalid id for photo detail route raises a 404."""
        response = self.client.get(reverse_lazy('photo_detail', kwargs={'id': 1000000000}))
        self.assertEqual(response.status_code, 404)

    def test_photo_detail_route_non_public_photo_raises_404(self):
        """Test that a non public photo for photo_detail_route raises a 404."""
        photo = Photo.objects.filter(published='PRIVATE').first()
        response = self.client.get(reverse_lazy('photo_detail', kwargs={'id': photo.id}))
        self.assertEqual(response.status_code, 404)

    def test_photo_detail_route_valid_id_gets_correct_photo(self):
        """Test that photo_detail_route for valid id has correct photo."""
        photo = Photo.objects.filter(published='PUBLIC').first()
        response = self.client.get(reverse_lazy('photo_detail', kwargs={'id': photo.id}))
        self.assertIn(photo.title.encode('utf8'), response.content)

    def test_album_detail_route_invalid_id_raises_404(self):
        """Test that an invalid id for album detail route raises a 404."""
        response = self.client.get(reverse_lazy('album_detail', kwargs={'id': 1000000000}))
        self.assertEqual(response.status_code, 404)

    def test_album_detail_route_non_public_album_raises_404(self):
        """Test that a non public album for album_detail_route raises a 404."""
        album = Album.objects.filter(published='PRIVATE').first()
        response = self.client.get(reverse_lazy('album_detail', kwargs={'id': album.id}))
        self.assertEqual(response.status_code, 404)

    def test_album_detail_route_valid_id_gets_correct_album(self):
        """Test that album_detail_route for valid id has correct album."""
        album = Album.objects.filter(published='PUBLIC').first()
        response = self.client.get(reverse_lazy('album_detail', kwargs={'id': album.id}))
        self.assertIn(album.title.encode('utf8'), response.content)

    def test_photo_create_route_get_no_login_has_302(self):
        """Test that photo create route get with no login has 302 code."""
        response = self.client.get(reverse_lazy('photo_create'))
        self.assertEqual(response.status_code, 302)

    def test_photo_create_route_get_no_login_redirects_login(self):
        """Test that photo create route get with no login redirects login."""
        response = self.client.get(reverse_lazy('photo_create'), follow=True)
        self.assertIn(b'Login</h1>', response.content)

    def test_photo_create_route_get_login_has_200(self):
        """Test that photo create route get with login has 200 code."""
        self.client.login(username='bob', password='password')
        response = self.client.get(reverse_lazy('photo_create'))
        self.assertEqual(response.status_code, 200)

    def test_photo_create_route_get_login_has_create_form(self):
        """Test that photo create route get with login has create form."""
        self.client.login(username='bob', password='password')
        response = self.client.get(reverse_lazy('photo_create'))
        self.assertIn(b'Upload New Photo', response.content)

    def test_photo_create_route_post_no_login_has_302(self):
        """Test that photo create route post with no login has 302 code."""
        response = self.client.post(reverse_lazy('photo_create'))
        self.assertEqual(response.status_code, 302)

    def test_photo_create_route_post_no_login_redirects_login(self):
        """Test that photo create route post with no login redirects login."""
        response = self.client.post(reverse_lazy('photo_create'), follow=True)
        self.assertIn(b'Login</h1>', response.content)

    @override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR,
                                               "test_media_for_photo_route"))
    def test_photo_create_route_post_login_has_302(self):
        """Test that photo create route post with login has 302 code."""
        self.client.login(username='bob', password='password')
        image = SimpleUploadedFile(
            name='sample_img.jpg',
            content=open(
                os.path.join(settings.BASE_DIR, 'static/test_image.jpg'), 'rb'
            ).read(),
            content_type="image/jpeg"
        )
        data = {
            'title': 'test',
            'description': 'testing',
            'image': image,
            'published': 'PRIVATE'
        }
        response = self.client.post(reverse_lazy('photo_create'), data)
        self.assertEqual(response.status_code, 302)

    @override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR,
                                               "test_media_for_photo_route"))
    def test_photo_create_route_post_login_redirects_library(self):
        """Test that photo create route post with login redirects library."""
        self.client.login(username='bob', password='password')
        image = SimpleUploadedFile(
            name='sample_img.jpg',
            content=open(
                os.path.join(settings.BASE_DIR, 'static/test_image.jpg'), 'rb'
            ).read(),
            content_type="image/jpeg"
        )
        data = {
            'title': 'test2',
            'description': 'testing2',
            'image': image,
            'published': 'PRIVATE'
        }
        response = self.client.post(reverse_lazy('photo_create'), data, follow=True)
        self.assertIn(b'<h1>Library</h1>', response.content)

    @override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR,
                                               "test_media_for_photo_route"))
    def test_photo_create_route_post_login_creates_new_photo(self):
        """Test that photo create route post with login creates a new photo."""
        self.client.login(username='bob', password='password')
        image = SimpleUploadedFile(
            name='sample_img.jpg',
            content=open(
                os.path.join(settings.BASE_DIR, 'static/test_image.jpg'), 'rb'
            ).read(),
            content_type="image/jpeg"
        )
        data = {
            'title': 'test3',
            'description': 'testing3',
            'image': image,
            'published': 'PRIVATE'
        }
        self.client.post(reverse_lazy('photo_create'), data)
        photo = Photo.objects.get(title='test3')
        self.assertIsNotNone(photo)
        self.assertEqual(photo.description, 'testing3')

    @override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR,
                                               "test_media_for_photo_route"))
    def test_photo_create_route_post_login_bad_data_has_200(self):
        """Test that photo create route post with login has 200 code."""
        self.client.login(username='bob', password='password')
        data = {
            'title': 'test',
            'description': 'testing',
            'published': 'PRIVATE'
        }
        response = self.client.post(reverse_lazy('photo_create'), data)
        self.assertEqual(response.status_code, 200)

    @override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR,
                                               "test_media_for_photo_route"))
    def test_photo_create_route_post_login_bad_data_has_error(self):
        """Test that photo create route post with login has error."""
        self.client.login(username='bob', password='password')
        data = {
            'title': 'test2',
            'description': 'testing2',
            'published': 'PRIVATE'
        }
        response = self.client.post(reverse_lazy('photo_create'), data)
        self.assertIn(b'class="errorlist"', response.content)

    def test_album_create_route_get_no_login_has_302(self):
        """Test that album create route get with no login has 302 code."""
        response = self.client.get(reverse_lazy('album_create'))
        self.assertEqual(response.status_code, 302)

    def test_album_create_route_get_no_login_redirects_login(self):
        """Test that album create route get with no login redirects login."""
        response = self.client.get(reverse_lazy('album_create'), follow=True)
        self.assertIn(b'Login</h1>', response.content)

    def test_album_create_route_get_login_has_200(self):
        """Test that album create route get with login has 200 code."""
        self.client.login(username='bob', password='password')
        response = self.client.get(reverse_lazy('album_create'))
        self.assertEqual(response.status_code, 200)

    def test_album_create_route_get_login_has_create_form(self):
        """Test that album create route get with login has create form."""
        self.client.login(username='bob', password='password')
        response = self.client.get(reverse_lazy('album_create'))
        self.assertIn(b'Create New Album', response.content)

    def test_album_create_route_post_no_login_has_302(self):
        """Test that album create route post with no login has 302 code."""
        response = self.client.post(reverse_lazy('album_create'))
        self.assertEqual(response.status_code, 302)

    def test_album_create_route_post_no_login_redirects_login(self):
        """Test that album create route post with no login redirects login."""
        response = self.client.post(reverse_lazy('album_create'), follow=True)
        self.assertIn(b'Login</h1>', response.content)

    def test_album_create_route_post_login_has_302(self):
        """Test that album create route post with login has 302 code."""
        self.client.login(username='bob', password='password')
        data = {
            'title': 'test',
            'description': 'testing',
            'cover': '',
            'photos': ['2'],
            'published': 'PRIVATE'
        }
        response = self.client.post(reverse_lazy('album_create'), data)
        self.assertEqual(response.status_code, 302)

    def test_album_create_route_post_login_redirects_library(self):
        """Test that album create route post with login redirects library."""
        self.client.login(username='bob', password='password')
        data = {
            'title': 'test2',
            'description': 'testing2',
            'cover': '',
            'photos': ['2'],
            'published': 'PRIVATE'
        }
        response = self.client.post(reverse_lazy('album_create'), data, follow=True)
        self.assertIn(b'<h1>Library</h1>', response.content)

    def test_album_create_route_post_login_creates_new_album(self):
        """Test that album create route post with login creates a new album."""
        self.client.login(username='bob', password='password')
        data = {
            'title': 'test3',
            'description': 'testing3',
            'cover': '',
            'photos': ['2'],
            'published': 'PRIVATE'
        }
        self.client.post(reverse_lazy('album_create'), data)
        album = Album.objects.get(title='test3')
        self.assertIsNotNone(album)
        self.assertEqual(album.description, 'testing3')

    def test_album_create_route_post_login_bad_data_has_200(self):
        """Test that album create route post with login has 200 code."""
        self.client.login(username='bob', password='password')
        data = {
            'title': 'test',
            'description': 'testing',
            'cover': '',
            'published': 'PRIVATE'
        }
        response = self.client.post(reverse_lazy('album_create'), data)
        self.assertEqual(response.status_code, 200)

    def test_album_create_route_post_login_bad_data_has_error(self):
        """Test that album create route post with login has error."""
        self.client.login(username='bob', password='password')
        data = {
            'title': 'test',
            'description': 'testing',
            'cover': '',
            'published': 'PRIVATE'
        }
        response = self.client.post(reverse_lazy('album_create'), data)
        self.assertIn(b'class="errorlist"', response.content)

    def test_photo_edit_route_get_bad_id_gets_404(self):
        """Test get to photo edit route for bad id has 404 code."""
        self.client.login(username='bob', password='password')
        response = self.client.get(reverse_lazy('photo_edit', kwargs={'id': 1000000000}))
        self.assertEqual(response.status_code, 404)

    def test_photo_edit_route_get_not_logged_in_has_302(self):
        """Test get to photo edit route when not logged in has 302 code."""
        response = self.client.get(reverse_lazy('photo_edit', kwargs={'id': 5}))
        self.assertEqual(response.status_code, 302)

    def test_photo_edit_route_get_not_logged_in_redirects_to_login(self):
        """Test get to photo edit route when not logged in redirects to login."""
        response = self.client.get(reverse_lazy('photo_edit', kwargs={'id': 5}), follow=True)
        self.assertIn(b'Login</h1>', response.content)

    def test_photo_edit_route_get_logged_in_has_200(self):
        """Test get to photo edit route when logged in has 200 code."""
        self.client.login(username='bob', password='password')
        response = self.client.get(reverse_lazy('photo_edit', kwargs={'id': 5}))
        self.assertEqual(response.status_code, 200)

    def test_photo_edit_route_get_logged_in_has_edit_form(self):
        """Test get to photo edit route when logged in has edit form."""
        self.client.login(username='bob', password='password')
        response = self.client.get(reverse_lazy('photo_edit', kwargs={'id': 5}))
        self.assertIn(b'Edit Photo</h1>', response.content)

    def test_photo_edit_route_post_bad_id_gets_404(self):
        """Test get to photo edit route for bad id has 404 code."""
        self.client.login(username='bob', password='password')
        response = self.client.post(reverse_lazy('photo_edit', kwargs={'id': 1000000000}))
        self.assertEqual(response.status_code, 404)

    def test_photo_edit_route_post_not_logged_in_has_302(self):
        """Test post to photo edit route when not logged in has 302 code."""
        response = self.client.post(reverse_lazy('photo_edit', kwargs={'id': 5}))
        self.assertEqual(response.status_code, 302)

    def test_photo_edit_route_post_not_logged_in_redirects_to_login(self):
        """Test post to photo edit route when not logged in redirects to login."""
        response = self.client.post(reverse_lazy('photo_edit', kwargs={'id': 5}), follow=True)
        self.assertIn(b'Login</h1>', response.content)

    @override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR,
                                               "test_media_for_photo_route"))
    def test_photo_edit_route_post_logged_in_has_302(self):
        """Test post to photo edit route when logged in has 302 code."""
        self.client.login(username='bob', password='password')
        image = SimpleUploadedFile(
            name='sample_img.jpg',
            content=open(
                os.path.join(settings.BASE_DIR, 'static/test_image.jpg'), 'rb'
            ).read(),
            content_type="image/jpeg"
        )
        data = {
            'title': 'test4',
            'description': 'testing4',
            'image': image,
            'published': 'PRIVATE'
        }
        response = self.client.post(reverse_lazy('photo_edit', kwargs={'id': 5}), data)
        self.assertEqual(response.status_code, 302)

    @override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR,
                                               "test_media_for_photo_route"))
    def test_photo_edit_route_post_logged_in_updates_the_correct_photo(self):
        """Test photo edit route post logged in updates the users photo."""
        self.client.login(username='bob', password='password')
        original_photo = Photo.objects.get(id=5)
        image = SimpleUploadedFile(
            name='sample_img.jpg',
            content=open(
                os.path.join(settings.BASE_DIR, 'static/test_image.jpg'), 'rb'
            ).read(),
            content_type="image/jpeg"
        )
        data = {
            'title': 'test5',
            'description': 'testing5',
            'image': image,
            'published': 'PRIVATE'
        }
        self.client.post(reverse_lazy('photo_edit', kwargs={'id': 5}), data)
        photo = Photo.objects.get(id=5)
        self.assertEqual(photo.title, 'test5')
        self.assertEqual(photo.description, 'testing5')
        self.assertIsNot(photo.image, original_photo.image)

    def test_photo_edit_route_post_logged_in_public_adds_published_date(self):
        """Test photo edit route post logged in set published to public sets published date."""
        self.client.login(username='bob', password='password')
        data = {
            'published': 'PUBLIC'
        }
        self.client.post(reverse_lazy('photo_edit', kwargs={'id': 5}), data)
        photo = Photo.objects.get(id=5)
        now = datetime.now().strftime('%x %X')[:2]
        self.assertEqual(photo.published, 'PUBLIC')
        self.assertEqual(photo.date_published.strftime('%x %X')[:2], now)

    @override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR,
                                               "test_media_for_photo_route"))
    def test_photo_edit_route_post_logged_in_done_redirects_to_library(self):
        """Test post to photo edit route when logged in redirects to library when done."""
        self.client.login(username='bob', password='password')
        image = SimpleUploadedFile(
            name='sample_img.jpg',
            content=open(
                os.path.join(settings.BASE_DIR, 'static/test_image.jpg'), 'rb'
            ).read(),
            content_type="image/jpeg"
        )
        data = {
            'title': 'test6',
            'description': 'testing6',
            'image': image,
            'published': 'PRIVATE'
        }
        response = self.client.post(reverse_lazy('photo_edit', kwargs={'id': 5}), data, follow=True)
        self.assertIn(b'<h1>Library</h1>', response.content)

    @override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR,
                                               "test_media_for_photo_route"))
    def test_photo_edit_route_post_logged_in_bad_data_has_200(self):
        """Test that photo create route post with login has 200 code."""
        self.client.login(username='bob', password='password')
        data = {}
        response = self.client.post(reverse_lazy('photo_edit', kwargs={'id': 5}), data)
        self.assertEqual(response.status_code, 200)

    @override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR,
                                               "test_media_for_photo_route"))
    def test_photo_edit_route_post_login_bad_data_has_error(self):
        """Test that photo create route post with login has error."""
        self.client.login(username='bob', password='password')
        data = {}
        response = self.client.post(reverse_lazy('photo_edit', kwargs={'id': 5}), data)
        self.assertIn(b'class="errorlist"', response.content)

    def test_album_edit_route_get_bad_id_gets_404(self):
        """Test get to album edit route for bad id has 404 code."""
        self.client.login(username='bob', password='password')
        response = self.client.get(reverse_lazy('album_edit', kwargs={'id': 1000000000}))
        self.assertEqual(response.status_code, 404)

    def test_album_edit_route_get_not_logged_in_has_302(self):
        """Test get to album edit route when not logged in has 302 code."""
        response = self.client.get(reverse_lazy('album_edit', kwargs={'id': 1}))
        self.assertEqual(response.status_code, 302)

    def test_album_edit_route_get_not_logged_in_redirects_to_login(self):
        """Test get to album edit route when not logged in redirects to login."""
        response = self.client.get(reverse_lazy('album_edit', kwargs={'id': 1}), follow=True)
        self.assertIn(b'Login</h1>', response.content)

    def test_album_edit_route_get_logged_in_has_200(self):
        """Test get to album edit route when logged in has 200 code."""
        self.client.login(username='bob', password='password')
        response = self.client.get(reverse_lazy('album_edit', kwargs={'id': 1}))
        self.assertEqual(response.status_code, 200)

    def test_album_edit_route_get_logged_in_has_edit_form(self):
        """Test get to album edit route when logged in has edit form."""
        self.client.login(username='bob', password='password')
        response = self.client.get(reverse_lazy('album_edit', kwargs={'id': 1}))
        self.assertIn(b'Edit Album</h1>', response.content)

    def test_album_edit_route_post_bad_id_gets_404(self):
        """Test get to album edit route for bad id has 404 code."""
        self.client.login(username='bob', password='password')
        response = self.client.post(reverse_lazy('album_edit', kwargs={'id': 1000000000}))
        self.assertEqual(response.status_code, 404)

    def test_album_edit_route_post_not_logged_in_has_302(self):
        """Test post to album edit route when not logged in has 302 code."""
        response = self.client.post(reverse_lazy('album_edit', kwargs={'id': 1}))
        self.assertEqual(response.status_code, 302)

    def test_album_edit_route_post_not_logged_in_redirects_to_login(self):
        """Test post to album edit route when not logged in redirects to login."""
        response = self.client.post(reverse_lazy('album_edit', kwargs={'id': 1}), follow=True)
        self.assertIn(b'Login</h1>', response.content)

    def test_album_edit_route_post_logged_in_has_302(self):
        """Test post to album edit route when logged in has 302 code."""
        self.client.login(username='bob', password='password')
        data = {
            'title': 'test4',
            'description': 'testing4',
            'published': 'PRIVATE',
            'photos': ['4']
        }
        response = self.client.post(reverse_lazy('album_edit', kwargs={'id': 1}), data)
        self.assertEqual(response.status_code, 302)

    def test_album_edit_route_post_logged_in_updates_the_correct_album(self):
        """Test album edit route post logged in updates the users album."""
        self.client.login(username='bob', password='password')
        data = {
            'title': 'test5',
            'description': 'testing5',
            'published': 'PRIVATE',
            'photos': ['5']
        }
        self.client.post(reverse_lazy('album_edit', kwargs={'id': 1}), data)
        album = Album.objects.get(id=1)
        self.assertEqual(album.title, 'test5')
        self.assertEqual(album.description, 'testing5')

    def test_album_edit_route_post_logged_in_public_adds_published_date(self):
        """Test album edit route post logged in set published to public sets published date."""
        self.client.login(username='bob', password='password')
        data = {
            'published': 'PUBLIC',
            'photos': ['1']
        }
        self.client.post(reverse_lazy('album_edit', kwargs={'id': 1}), data)
        album = Album.objects.get(id=1)
        now = datetime.now().strftime('%x %X')[:2]
        self.assertEqual(album.published, 'PUBLIC')
        self.assertEqual(album.date_published.strftime('%x %X')[:2], now)

    def test_album_edit_route_post_logged_in_done_redirects_to_library(self):
        """Test post to album edit route when logged in redirects to library when done."""
        self.client.login(username='bob', password='password')
        data = {
            'title': 'test6',
            'description': 'testing6',
            'published': 'PRIVATE',
            'photos': ['6']
        }
        response = self.client.post(reverse_lazy('album_edit', kwargs={'id': 1}), data, follow=True)
        self.assertIn(b'<h1>Library</h1>', response.content)

    def test_album_edit_route_post_logged_in_bad_data_has_200(self):
        """Test that album create route post with login has 200 code."""
        self.client.login(username='bob', password='password')
        data = {}
        response = self.client.post(reverse_lazy('album_edit', kwargs={'id': 1}), data)
        self.assertEqual(response.status_code, 200)

    def test_album_edit_route_post_login_bad_data_has_error(self):
        """Test that album create route post with login has error."""
        self.client.login(username='bob', password='password')
        data = {}
        response = self.client.post(reverse_lazy('album_edit', kwargs={'id': 1}), data)
        self.assertIn(b'class="errorlist"', response.content)
