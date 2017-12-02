"""Tests for the Photo and Album models."""
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import Http404
from django.test import override_settings, RequestFactory, TestCase
from django.urls import reverse_lazy
from imager_images.models import Photo, Album
from imager_profile.models import User
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
        self.assertEqual(str(one_photo), 'Photo: wedding')

    def test_album_to_string_is_correct(self):
        """Test that the __str__ method returns the album title."""
        one_album = Album.objects.get(title='first')
        self.assertEqual(str(one_album), 'Album: first')

    def test_all_photos_are_added_to_the_database(self):
        """Test that all created photos are added to the database."""
        self.assertEqual(Photo.objects.count(), 36)

    @override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR,
                                               "test_media_for_photos"))
    def test_all_photos_are_added_to_the_media_directory(self):
        """Test that all created photos are added to the media directory."""
        path = os.path.join(settings.MEDIA_ROOT, 'images')
        files = [name for name in os.listdir(path) if name.endswith('.jpg')]
        self.assertEqual(len(files), 36)

    def test_photos_are_added_to_an_album(self):
        """Test that all created photos are added to the database."""
        photos = Photo.objects.filter(albums__title='first').count()
        self.assertEqual(photos, 15)

    def test_photo_has_user(self):
        """Test that the photo has a user."""
        one_photo = Photo.objects.get(title='wedding')
        one_user = User.objects.first()
        self.assertEqual(one_photo.user, one_user)

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

    def test_photo_has_date_published(self):
        """Test that the photo has a date-published that is None by default."""
        one_photo = Photo.objects.get(title='wedding')
        self.assertIsNone(one_photo.date_published)

    def test_all_albums_are_added_to_the_database(self):
        """Test that all created albums are added to the database."""
        self.assertEqual(Album.objects.count(), 2)

    def test_album_has_user(self):
        """Test that the album has a user."""
        one_album = Album.objects.get(title='first')
        one_user = User.objects.first()
        self.assertEqual(one_album.user, one_user)

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

    def test_album_has_date_published(self):
        """Test that the album has a date-published that is None by default."""
        one_album = Album.objects.get(title='first')
        self.assertIsNone(one_album.date_published)


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

    def test_library_view_redirects_home_not_logged_in(self):
        """Test that library_view redirects home if not logged in."""
        from imager_images.views import LibraryView
        request = self.request.get('')
        request.user = AnonymousUser()
        view = LibraryView(request=request)
        response = view.get()
        self.assertEqual(response.status_code, 302)

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

    def test_library_route_redirects_home_not_logged_in(self):
        """Test that library route redirects home if not logged in."""
        response = self.client.get(reverse_lazy('library'), follow=True)
        self.assertIn(b'<h1>Imager</h1>', response.content)

    def test_library_route_logged_in_displays_all_photos_and_albums(self):
        """Test that library route displays all logged in user's things."""
        self.client.login(username='bob', password='password')
        response = self.client.get(reverse_lazy('library'))
        image_count = response.content.count(b'<img')
        self.assertEqual(image_count, 17)

    def test_photo_gallery_route_has_all_public_photos(self):
        """Test that the photo gallery route has all public photos."""
        response = self.client.get(reverse_lazy('photo_gallery'))
        image_count = response.content.count(b'<img')
        self.assertEqual(image_count, 23)

    def test_album_gallery_route_has_all_public_albums(self):
        """Test that the album gallery route has all public albums."""
        response = self.client.get(reverse_lazy('album_gallery'))
        image_count = response.content.count(b'<img')
        self.assertEqual(image_count, 2)

    def test_photo_detail_route_invalid_id_raises_404(self):
        """Test that an invalid id for photo detail route raises a 404."""
        response = self.client.get('/images/photos/1000000000/')
        self.assertEqual(response.status_code, 404)

    def test_photo_detail_route_non_public_photo_raises_404(self):
        """Test that a non public photo for photo_detail_route raises a 404."""
        photo = Photo.objects.filter(published='PRIVATE').first()
        response = self.client.get('/images/photos/{}'.format(photo.id))
        self.assertEqual(response.status_code, 404)

    def test_photo_detail_route_valid_id_gets_correct_photo(self):
        """Test that photo_detail_route for valid id has correct photo."""
        photo = Photo.objects.filter(published='PUBLIC').first()
        response = self.client.get('/images/photos/{}'.format(photo.id))
        self.assertIn(photo.title.encode('utf8'), response.content)

    def test_album_detail_route_invalid_id_raises_404(self):
        """Test that an invalid id for album detail route raises a 404."""
        response = self.client.get('/images/albums/1000000000/')
        self.assertEqual(response.status_code, 404)

    def test_album_detail_route_non_public_album_raises_404(self):
        """Test that a non public album for album_detail_route raises a 404."""
        album = Album.objects.filter(published='PRIVATE').first()
        response = self.client.get('/images/albums/{}'.format(album.id))
        self.assertEqual(response.status_code, 404)

    def test_album_detail_route_valid_id_gets_correct_album(self):
        """Test that album_detail_route for valid id has correct album."""
        album = Album.objects.filter(published='PUBLIC').first()
        response = self.client.get('/images/albums/{}'.format(album.id))
        self.assertIn(album.title.encode('utf8'), response.content)
