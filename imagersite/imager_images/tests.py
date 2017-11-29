"""Tests for the Photo and Album models."""
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from imager_images.models import Photo, Album
from imager_profile.models import User
from imager_profile.tests import UserFactory

from datetime import datetime
import factory
import os
import random


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
    published = random.choice(['PRIVATE', 'SHARED', 'PUBLIC'])


class AlbumFactory(factory.django.DjangoModelFactory):
    """Factory for fake Album."""

    class Meta:
        """Meta."""

        model = Album

    title = factory.Faker('word')
    description = factory.Faker('sentence')
    published = random.choice(['PRIVATE', 'SHARED', 'PUBLIC'])


class PhotoAlbumTests(TestCase):
    """Tests for the imager_profile module."""

    @classmethod
    @override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR, "test_media_for_photos"))
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

    def test_all_photos_are_added_to_the_database(self):
        """Test that all created photos are added to the database."""
        self.assertEqual(Photo.objects.count(), 36)

    @override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR, "test_media_for_photos"))
    def test_all_photos_are_added_to_the_media_directory(self):
        """Test that all created photos are added to the media directory."""
        path = os.path.join(settings.MEDIA_ROOT, 'images')
        files = [name for name in os.listdir(path) if name.endswith('.jpg')]
        self.assertEqual(len(files), 36)

    def test_photos_are_added_to_an_album(self):
        """Test that all created photos are added to the database."""
        self.assertEqual(Photo.objects.filter(albums__title='first').count(), 15)

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

    @override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR, "test_media_for_photos"))
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

    @override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR, "test_media_for_photos"))
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
