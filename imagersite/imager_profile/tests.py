"""."""
from django.test import TestCase
from imager_profile.models import ImagerProfile, User

# Create your tests here.


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

        user = User(username='bob2', email='bob2@bob.net')
        user.set_password('password')
        user.save()
        profile = ImagerProfile(website='www.timey.net',
                                location='here',
                                fee=10.00,
                                bio='I hate photography.',
                                phone='123-4567',
                                user=user,
                                is_active=False)
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
