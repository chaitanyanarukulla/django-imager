"""Tests for the ImagerProfile models."""
from django.test import TestCase
from imager_profile.models import ImagerProfile, User

import factory
import random


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for fake User."""

    class Meta:
        model = User

    username = factory.Sequence(lambda n:
                                '{}{}'.format(factory.Faker('first_name'), n))
    email = factory.Faker('email')


class ProfileFactory(factory.django.DjangoModelFactory):
    """Factory for fake ImagerProfile."""

    class Meta:
        model = ImagerProfile

    website = factory.Faker('url')
    location = factory.Faker('address')
    fee = random.uniform(0, 100)
    bio = factory.Faker('paragraph')
    phone = factory.Faker('phone_number')


class ProfileTests(TestCase):
    """Tests for the imager_profile module."""

    def setUp(self):
        """Add one minimal user to the database."""
        user = User(username='bob', email='bob@bob.net')
        user.set_password('password')
        user.save()
        profile = ImagerProfile(website='www.fun.net',
                                location='nowhere',
                                fee=20.00,
                                bio='I photograph things all the time.',
                                phone='123-4567',
                                user=user)
        profile.save()

        user = UserFactory.create()
        user.set_password(factory.Faker('password'))
        user.save()
        profile = ProfileFactory.create(user=user, is_active=False)
        profile.save()

        for _ in range(10):
            user = UserFactory.create()
            user.set_password(factory.Faker('password'))
            user.save()
            profile = ProfileFactory.create(user=user)
            profile.save()

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
        self.assertEquals(ImagerProfile.objects.all().count(), 12)

    def test_all_users_created(self):
        """Test that all users were added to the database."""
        self.assertEquals(User.objects.all().count(), 12)
