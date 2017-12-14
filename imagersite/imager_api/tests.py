from django.conf import settings
from django.test import override_settings, RequestFactory, TestCase
from django.urls import reverse_lazy
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


class PhotoAPIRouteTests(TestCase):
    """Route tests for the imager_api app."""

    @classmethod
    @override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR,
                                               "test_media_for_photos_api_routes"))
    def setUpClass(cls):
        """Add one minimal user to the database."""
        super(PhotoAPIRouteTests, cls).setUpClass()

        os.system('mkdir {}'.format(
            os.path.join(settings.BASE_DIR, 'test_media_for_photos_api_routes')
        ))

        user = UserFactory(username='bob')
        user.set_password('password')
        user.save()
        cls.user = user

        for _ in range(10):
            photo = PhotoFactory(user=user)
            photo.save()

        user = UserFactory()
        user.set_password(factory.Faker('password'))
        user.save()
        cls.second_user = user

        for _ in range(5):
            photo = PhotoFactory(user=user)
            photo.save()

    @classmethod
    def tearDownClass(cls):
        """Remove the test directory."""
        super(PhotoAPIRouteTests, cls).tearDownClass()
        os.system('rm -rf {}'.format(
            os.path.join(settings.BASE_DIR, 'test_media_for_photos_api_routes')))

    def test_photos_api_route_not_logged_in_gets_403(self):
        """Test photos API route gets a 403 status code if not logged in."""
        response = self.client.get(reverse_lazy('api_photo_list'))
        self.assertEqual(response.status_code, 403)

    def test_photos_api_route_logged_in_gets_200(self):
        """Test photos API route gets a 200 status code if logged in."""
        self.client.login(username='bob', password='password')
        response = self.client.get(reverse_lazy('api_photo_list'))
        self.assertEqual(response.status_code, 200)

    def test_photos_api_route_logged_in_gets_all_users_photos(self):
        """Test photos API route gets all the user's photos if logged in."""
        self.client.login(username='bob', password='password')
        response = self.client.get(reverse_lazy('api_photo_list'))
        self.assertEqual(len(response.json()), 10)

    def test_photos_api_route_logged_in_gets_users_photos(self):
        """Test photos API route gets the user's photos if logged in."""
        self.client.login(username='bob', password='password')
        response = self.client.get(reverse_lazy('api_photo_list'))
        ids = [photo['id'] for photo in response.json()]
        for photo in self.user.photos.all():
            self.assertIn(photo.id, ids)

    def test_photos_api_route_logged_in_gets_not_other_users_photos(self):
        """Test photos API route does not get other user's photos if logged in."""
        self.client.login(username='bob', password='password')
        response = self.client.get(reverse_lazy('api_photo_list'))
        ids = [photo['id'] for photo in response.json()]
        for photo in self.second_user.photos.all():
            self.assertNotIn(photo.id, ids)
