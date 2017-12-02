"""Tests for the ImagerProfile models."""
from django.contrib.auth.models import AnonymousUser
from django.http import Http404
from django.test import TestCase, RequestFactory
from faker import Faker
from imager_profile.models import ImagerProfile, User

import factory
import random


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for fake User."""

    class Meta:
        """Meta."""

        model = User

    username = factory.Sequence(lambda n:
                                '{}{}'.format(factory.Faker('first_name'), n))
    email = factory.Faker('email')


def fillout_profile(profile, website=None, location=None, fee=None,
                    bio=None, phone=None, is_active=None):
    """Fill out an empty profile."""
    fake = Faker()
    profile.website = website if website else fake.url()
    profile.location = location if location else fake.address()
    profile.fee = fee if fee is not None else random.uniform(0, 100)
    profile.bio = bio if bio else fake.paragraph()
    profile.phone = phone if phone else fake.phone_number()
    if is_active is not None:
        profile.is_active = is_active


class ProfileTests(TestCase):
    """Tests for the imager_profile module."""

    @classmethod
    def setUpClass(cls):
        """Add one minimal user to the database."""
        super(ProfileTests, cls).setUpClass()
        user = UserFactory(username='bob', email='bob@bob.net')
        user.set_password('password')
        user.save()
        fillout_profile(user.profile,
                        website='www.fun.net',
                        location='nowhere',
                        fee=20.00,
                        bio='I photograph things all the time.',
                        phone='123-4567')
        user.profile.save()

        user = UserFactory.create()
        user.set_password(factory.Faker('password'))
        user.save()
        fillout_profile(user.profile, is_active=False)
        user.profile.save()

        for _ in range(10):
            user = UserFactory.create()
            user.set_password(factory.Faker('password'))
            user.save()
            fillout_profile(user.profile)
            user.profile.save()

    def test_profile_to_string_is_correct(self):
        """Test that the __str__ method returns the profile username."""
        one_profile = ImagerProfile.objects.get(user__username='bob')
        self.assertEqual(str(one_profile), 'Profile: bob')

    def test_profile_is_created_when_user_is_saved(self):
        """Test that a profile is created automatically when a user is."""
        self.assertEquals(ImagerProfile.objects.count(), 12)
        user = UserFactory()
        user.set_password(factory.Faker('password'))
        user.save()
        self.assertEquals(ImagerProfile.objects.count(), 13)

    def test_profile_is_not_created_when_user_is_updated(self):
        """Test that a profile is created automatically when a user is."""
        self.assertEquals(ImagerProfile.objects.count(), 12)
        one_user = User.objects.last()
        one_user.username = 'Fred'
        one_user.save()
        self.assertEquals(ImagerProfile.objects.count(), 12)

    def test_profile_has_website(self):
        """Test that a profile has a website."""
        active_user = User.objects.get(username='bob')
        one_profile = ImagerProfile.objects.get(user=active_user)
        self.assertEquals(one_profile.website, 'www.fun.net')

    def test_profile_has_location(self):
        """Test that a profile has a location."""
        active_user = User.objects.get(username='bob')
        one_profile = ImagerProfile.objects.get(user=active_user)
        self.assertEquals(one_profile.location, 'nowhere')

    def test_profile_has_fee(self):
        """Test that a profile has a fee."""
        active_user = User.objects.get(username='bob')
        one_profile = ImagerProfile.objects.get(user=active_user)
        self.assertEquals(one_profile.fee, 20.00)

    def test_profile_has_bio(self):
        """Test that a profile has a bio."""
        active_user = User.objects.get(username='bob')
        one_profile = ImagerProfile.objects.get(user=active_user)
        self.assertEquals(one_profile.bio, 'I photograph things all the time.')

    def test_profile_has_phone(self):
        """Test that a profile has a phone."""
        active_user = User.objects.get(username='bob')
        one_profile = ImagerProfile.objects.get(user=active_user)
        self.assertEquals(one_profile.phone, '123-4567')

    def test_user_can_point_to_its_profile(self):
        """Test that a user and profile are connected."""
        one_user = User.objects.get(username='bob')
        self.assertIsNotNone(one_user.profile)

    def test_profile_is_active_by_default(self):
        """Test that a profile is active."""
        active_user = User.objects.get(username='bob')
        one_profile = ImagerProfile.objects.get(user=active_user)
        self.assertTrue(one_profile.is_active)

    def test_all_items_in_active(self):
        """Test that active method gets all active profiles."""
        active_profiles = ImagerProfile.active()
        all_profiles = ImagerProfile.objects.all()
        self.assertEquals(active_profiles.count(), all_profiles.count() - 1)

    def test_all_profiles_created(self):
        """Test that all profiles were added to the database."""
        self.assertEquals(ImagerProfile.objects.count(), 12)

    def test_all_users_created(self):
        """Test that all users were added to the database."""
        self.assertEquals(User.objects.count(), 12)


"""Tests for the Profile routes."""


class ProfileViewUnitTests(TestCase):
    """Tests for the view functions in imagersite."""

    def setUp(self):
        """Set up a dummy request."""
        self.request = RequestFactory()
        user = UserFactory(username='bob', email='bob@bob.net')
        user.set_password('password')
        user.save()
        self.bob = user
        fillout_profile(user.profile,
                        website='www.fun.net',
                        location='nowhere',
                        fee=20.00,
                        bio='I photograph things all the time.',
                        phone='123-4567')
        user.profile.save()

    def test_profile_view_with_user_name_gets_user_profile(self):
        """Test that the p_view function returns a page with user profile."""
        from imager_profile.views import profile_view
        request = self.request.get('')
        request.user = AnonymousUser()
        response = profile_view(request, 'bob')
        self.assertIn(b'I photograph things all the time.', response.content)

    def test_profile_view_with_no_user_name_not_logged_in_redirets_home(self):
        """Test profile_view with no user name not logged in redirets."""
        from imager_profile.views import profile_view
        request = self.request.get('')
        request.user = AnonymousUser()
        response = profile_view(request)
        self.assertEqual(response.status_code, 302)

    def test_profile_view_with_bad_user_returns_404(self):
        """Test profile_view with bad user returns 404."""
        from imager_profile.views import profile_view
        request = self.request.get('')
        request.user = AnonymousUser()
        with self.assertRaises(Http404):
            profile_view(request, 'don')

    def test_profile_view_with_logged_in_user_gets_user_profile(self):
        """Test profile_view with logged in user gets user profile."""
        from imager_profile.views import profile_view
        request = self.request.get('')
        request.user = self.bob
        response = profile_view(request)
        self.assertIn(b'I photograph things all the time.', response.content)


class ProfileRoutingTests(TestCase):
    """Tests for the routes in imagersite."""

    def setUp(self):
        """Set up a user for testing login.."""
        user = UserFactory(username='bob', email='bob@bob.net')
        user.set_password('password')
        user.save()
        self.bob = user
        fillout_profile(user.profile,
                        website='www.fun.net',
                        location='nowhere',
                        fee=20.00,
                        bio='I photograph things all the time.',
                        phone='123-4567')
        user.profile.save()

        user = UserFactory(username='rob', email='rob@rob.net')
        user.set_password('password')
        user.save()
        fillout_profile(user.profile,
                        website='www.funlikebob.net',
                        location='nowhereland',
                        fee=40.00,
                        bio='I photograph things all the time like bob.',
                        phone='123-4567-555')
        user.profile.save()

    def test_profile_route_has_200_response_given_a_user_name(self):
        """Test that profile route has a 200 response code."""
        response = self.client.get('/profile/bob')
        self.assertEqual(response.status_code, 200)

    def test_profile_route_has_given_user_info(self):
        """Test that profile route has a given user info."""
        response = self.client.get('/profile/bob')
        self.assertIn(b'I photograph things all the time.', response.content)

    def test_profile_route_doesnt_have_counts_for_given_user(self):
        """Test profile route doesnt have counts for given user."""
        response = self.client.get('/profile/bob')
        self.assertNotIn(b'Private:', response.content)

    def test_profile_route_has_200_response_if_user_logged_in(self):
        """Test that profile route has a 200 response code."""
        self.client.login(username='bob', password='password')
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 200)

    def test_profile_route_has_logged_in_user_info(self):
        """Test that profile route has a loggedin  user info."""
        self.client.login(username='bob', password='password')
        response = self.client.get('/profile/')
        self.assertIn(b'I photograph things all the time.', response.content)

    def test_profile_route_does_have_counts_for_loggedin_user(self):
        """Test profile route does have counts for loggedin user."""
        self.client.login(username='bob', password='password')
        response = self.client.get('/profile/')
        self.assertIn(b'Private:', response.content)

    def test_profile_route_has_given_user_info_when_logged_in(self):
        """Test that profile route has a given user loggedin."""
        self.client.login(username='bob', password='password')
        response = self.client.get('/profile/rob')
        self.assertIn(b'I photograph things all the time like bob.',
                      response.content)

    def test_profile_route_has_404_response_for_invalid_user(self):
        """Test profile route has 404 response for invalid user."""
        response = self.client.get('/profile/don')
        self.assertEqual(response.status_code, 404)

    def test_profile_route_redirets_home_not_loggedin_no_user(self):
        """Test profile route redirets home not loggedin no user."""
        response = self.client.get('/profile/', follow=True)
        self.assertIn(b'<h1>Imager</h1>', response.content)

    def test_profile_route_has_302_response_for_not_loggedin_no_user(self):
        """Test profile route has 302 response for not loggedin no user."""
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 302)
