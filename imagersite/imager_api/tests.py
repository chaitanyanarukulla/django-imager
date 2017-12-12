from django.conf import settings
from django.test import override_settings, RequestFactory, TestCase
from imager_images.tests import PhotoFactory
from imager_profile.tests import UserFactory
import factory
import os


class PhotoAPIUnitTests(TestCase):
    """Unit tests for the imager_api app."""

    @classmethod
    @override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR,
                                               "test_media_for_photos_api"))
    def setUpClass(cls):
        """Add one minimal user to the database."""
        super(PhotoAPIUnitTests, cls).setUpClass()

        os.system('mkdir {}'.format(
            os.path.join(settings.BASE_DIR, 'test_media_for_photos_api')
        ))

        cls.request = RequestFactory()

        user = UserFactory()
        user.set_password(factory.Faker('password'))
        user.save()
        cls.user = user

        for _ in range(10):
            photo = PhotoFactory(user=user)
            photo.save()

        user = UserFactory()
        user.set_password(factory.Faker('password'))
        user.save()
        for _ in range(5):
            photo = PhotoFactory(user=user)
            photo.save()

    @classmethod
    def tearDownClass(cls):
        """Remove the test directory."""
        super(PhotoAPIUnitTests, cls).tearDownClass()
        os.system('rm -rf {}'.format(
            os.path.join(settings.BASE_DIR, 'test_media_for_photos_api')))

    def test_serializer_has_all_photo_fields(self):
        """Test that all fields from the photo model are on the serializer."""
        from imager_api.serializers import PhotoSerializer
        serializer = PhotoSerializer()
        for key in ['id', 'image', 'title', 'description', 'date_uploaded',
                    'date_modified', 'date_published', 'published']:
            self.assertIn(key, serializer.fields)

    def test_photolist_get_queryset_has_only_photos_for_current_user(self):
        """Test that the queryset only has the photos of the authN user."""
        from imager_api.views import PhotoListAPI
        request = self.request.get('')
        request.user = self.user
        view = PhotoListAPI(request=request)
        photos = view.get_queryset()
        self.assertEqual(photos.count(), self.user.photos.count())
