"""Tests for the ImagerProfile models."""
from django.test import TestCase
from imager_profile.models import ImagerProfile, User

import factory
from faker import Faker
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
