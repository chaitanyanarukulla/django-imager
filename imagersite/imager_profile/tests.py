"""Tests for the ImagerProfile models."""
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, RequestFactory
from django.urls import reverse_lazy
from faker import Faker
from imager_profile.models import ImagerProfile, ImagerProfileForm, User

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
        user.first_name = 'Bob'
        user.last_name = 'Ross'
        user.save()
        cls.bob = user
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

    def test_profile_form_has_user_fields(self):
        """Test profile form has user fields."""
        form = ImagerProfileForm(username=self.bob.username)
        self.assertIn('email', form.fields)
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)

    def test_profile_form_has_user_fields_filled_from_user(self):
        """Test profile form has user fields."""
        form = ImagerProfileForm(username=self.bob.username)
        self.assertEqual(self.bob.email, form.fields['email'].initial)
        self.assertEqual(self.bob.first_name, form.fields['first_name'].initial)
        self.assertEqual(self.bob.last_name, form.fields['last_name'].initial)


"""Unit tests for the Profile view classes."""


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
        from imager_profile.views import ProfileView
        request = self.request.get('')
        request.user = AnonymousUser()
        view = ProfileView(request=request, kwargs={'username': 'bob'})
        response = view.get(request)
        response.render()
        self.assertIn(b'I photograph things all the time.', response.content)

    def test_profile_view_with_user_name_gets_user_profile_even_with_slash(self):
        """Test that the p_view function returns a page with user profile."""
        from imager_profile.views import ProfileView
        request = self.request.get('')
        request.user = AnonymousUser()
        view = ProfileView(request=request, kwargs={'username': 'bob/'})
        response = view.get(request)
        response.render()
        self.assertIn(b'I photograph things all the time.', response.content)

    def test_profile_view_with_no_user_name_not_logged_in_redirets_home(self):
        """Test profile_view with no user name not logged in redirets."""
        from imager_profile.views import ProfileView
        request = self.request.get('')
        request.user = AnonymousUser()
        view = ProfileView(request=request, kwargs={'username': ''})
        response = view.get(request)
        self.assertEqual(response.status_code, 302)

    def test_profile_view_with_logged_in_user_gets_user_profile(self):
        """Test profile_view with logged in user gets user profile."""
        from imager_profile.views import ProfileView
        request = self.request.get('')
        request.user = self.bob
        view = ProfileView(request=request, kwargs={'username': ''})
        response = view.get(request)
        response.render()
        self.assertIn(b'I photograph things all the time.', response.content)

    def test_profile_view_get_context_has_view_photos_and_albums_for_owner(self):
        """Test that the context from ProfileView has all properties."""
        from imager_profile.views import ProfileView
        request = self.request.get('')
        request.user = self.bob
        view = ProfileView(request=request, object='')
        data = view.get_context_data(object=ImagerProfile.objects.first())
        self.assertIn('view', data)
        self.assertIn('photos', data)
        self.assertIn('albums', data)
        self.assertTrue(data['owner'])

    def test_profile_view_get_context_has_view_photos_and_albums_for_non_owner(self):
        """Test that the context from ProfileView has all properties."""
        from imager_profile.views import ProfileView
        request = self.request.get('')
        request.user = AnonymousUser()
        view = ProfileView(request=request, object='')
        data = view.get_context_data(object=ImagerProfile.objects.first())
        self.assertIn('view', data)
        self.assertIn('photos', data)
        self.assertIn('albums', data)
        self.assertFalse(data['owner'])

    def test_profile_edit_view_get_form_kwargs_assigns_current_user(self):
        """Test profile editview get form kwargs assigns current user."""
        from imager_profile.views import ProfileEditView
        request = self.request.get('')
        request.user = self.bob
        view = ProfileEditView(request=request)
        kwargs = view.get_form_kwargs()
        self.assertIn('username', kwargs)
        self.assertEqual(kwargs['username'], 'bob')

    def test_profile_edit_view_get_assigns_current_user(self):
        """Test profile editview get assigns current user."""
        from imager_profile.views import ProfileEditView
        request = self.request.get('')
        request.user = self.bob
        view = ProfileEditView(request=request, kwargs={})
        view.get(request)
        self.assertIn('username', view.kwargs)
        self.assertEqual(view.kwargs['username'], 'bob')

    def test_profile_edit_view_post_assigns_current_user(self):
        """Test profile editview post assigns current user."""
        from imager_profile.views import ProfileEditView
        request = self.request.post('')
        request.user = self.bob
        view = ProfileEditView(request=request, kwargs={})
        view.post(request)
        self.assertIn('username', view.kwargs)
        self.assertEqual(view.kwargs['username'], 'bob')

    def test_profile_edit_view_form_valid_update_current_user_object(self):
        """Test profile edit view form valid update current user object."""
        from imager_profile.views import ProfileEditView
        form_class = ImagerProfileForm
        request = self.request.post('')
        request.user = self.bob
        view = ProfileEditView(request=request)
        data = {'email': 'test@gmail.com', 'first_name': 'Rob',
                'last_name': 'Boss', 'camera': 'SLR', 'bio': '',
                'website': 'www.robBoss.com', 'phone': '',
                'location': '', 'fee': '20', 'services': '', 'photostyles': ''}
        profile = ImagerProfile.objects.get(user=request.user)
        form = form_class(data=data, username=request.user.username, instance=profile)
        form.is_valid()
        view.form_valid(form)
        updated_bob = User.objects.first()
        self.assertEqual(updated_bob.email, 'test@gmail.com')
        self.assertEqual(updated_bob.first_name, 'Rob')
        self.assertEqual(updated_bob.last_name, 'Boss')
        self.assertEqual(updated_bob.profile.fee, 20)


"""Tests for the Profile routes."""


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
        response = self.client.get(reverse_lazy('profile', kwargs={'username': 'bob'}))
        self.assertEqual(response.status_code, 200)

    def test_profile_route_has_given_user_info(self):
        """Test that profile route has a given user info."""
        response = self.client.get(reverse_lazy('profile', kwargs={'username': 'bob'}))
        self.assertIn(b'I photograph things all the time.', response.content)

    def test_profile_route_doesnt_have_counts_for_given_user(self):
        """Test profile route doesnt have counts for given user."""
        response = self.client.get(reverse_lazy('profile', kwargs={'username': 'bob'}))
        self.assertNotIn(b'Private:', response.content)

    def test_profile_route_has_200_response_if_user_logged_in(self):
        """Test that profile route has a 200 response code."""
        self.client.login(username='bob', password='password')
        response = self.client.get(reverse_lazy('profile', kwargs={'username': ''}))
        self.assertEqual(response.status_code, 200)

    def test_profile_route_has_logged_in_user_info(self):
        """Test that profile route has a loggedin  user info."""
        self.client.login(username='bob', password='password')
        response = self.client.get(reverse_lazy('profile', kwargs={'username': ''}))
        self.assertIn(b'I photograph things all the time.', response.content)

    def test_profile_route_does_have_counts_for_loggedin_user(self):
        """Test profile route does have counts for loggedin user."""
        self.client.login(username='bob', password='password')
        response = self.client.get(reverse_lazy('profile', kwargs={'username': ''}))
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
        response = self.client.get(reverse_lazy('profile', kwargs={'username': ''}), follow=True)
        self.assertIn(b'<h1>Imager</h1>', response.content)

    def test_profile_route_has_302_response_for_not_loggedin_no_user(self):
        """Test profile route has 302 response for not loggedin no user."""
        response = self.client.get(reverse_lazy('profile', kwargs={'username': ''}))
        self.assertEqual(response.status_code, 302)

    def test_profile_edit_route_get_not_logged_in_has_302(self):
        """Test get to profile edit route when not logged in has 302 code."""
        response = self.client.get(reverse_lazy('profile_edit'))
        self.assertEqual(response.status_code, 302)

    def test_profile_edit_route_get_not_logged_in_redirects_to_login(self):
        """Test get to profile edit route when not logged in redirects to login."""
        response = self.client.get(reverse_lazy('profile_edit'), follow=True)
        self.assertIn(b'Login</h1>', response.content)

    def test_profile_edit_route_get_logged_in_has_200(self):
        """Test get to profile edit route when logged in has 200 code."""
        self.client.login(username='bob', password='password')
        response = self.client.get(reverse_lazy('profile_edit'))
        self.assertEqual(response.status_code, 200)

    def test_profile_edit_route_get_logged_in_has_edit_form(self):
        """Test get to profile edit route when logged in has edit form."""
        self.client.login(username='bob', password='password')
        response = self.client.get(reverse_lazy('profile_edit'))
        self.assertIn(b'Edit Profile</h1>', response.content)

    def test_profile_edit_route_post_not_logged_in_has_302(self):
        """Test post to profile edit route when not logged in has 302 code."""
        response = self.client.post(reverse_lazy('profile_edit'))
        self.assertEqual(response.status_code, 302)

    def test_profile_edit_route_post_not_logged_in_redirects_to_login(self):
        """Test post to profile edit route when not logged in redirects to login."""
        response = self.client.post(reverse_lazy('profile_edit'), follow=True)
        self.assertIn(b'Login</h1>', response.content)

    def test_profile_edit_route_post_logged_in_has_302(self):
        """Test post to profile edit route when logged in has 302 code."""
        self.client.login(username='bob', password='password')
        data = {
            'email': 'notatest@gmail.com',
            'first_name': '',
            'last_name': '',
        }
        response = self.client.post(reverse_lazy('profile_edit'), data)
        self.assertEqual(response.status_code, 302)

    def test_profile_edit_route_post_logged_in_updates_the_users_profile(self):
        """Test profile edit route post logged in updates the users profile."""
        self.client.login(username='bob', password='password')
        data = {
            'email': 'test@hotmail.com',
            'first_name': 'Dan',
            'last_name': 'Theman',
            'camera': 'SLR',
            'bio': 'I am not bob or rob.',
            'website': 'www.theman.gov',
            'phone': '222-3222',
            'location': 'top of the world',
            'fee': '1000000',
            'services': ['weddings'],
            'photostyles': ['night']
        }
        self.client.post(reverse_lazy('profile_edit'), data)
        profile = ImagerProfile.objects.get(user=self.bob)
        self.assertEqual(profile.camera, 'SLR')
        self.assertEqual(profile.bio, 'I am not bob or rob.')
        self.assertEqual(profile.website, 'http://www.theman.gov')
        self.assertEqual(profile.phone, '222-3222')
        self.assertEqual(profile.location, 'top of the world')
        self.assertEqual(profile.fee, 1000000)
        self.assertIn('weddings', profile.services)
        self.assertIn('night', profile.photostyles)

    def test_profile_edit_route_post_logged_in_updates_the_user(self):
        """Test profile edit route post logged in updates the user."""
        self.client.login(username='bob', password='password')
        data = {
            'email': 'test@yahoo.com',
            'first_name': 'Man',
            'last_name': 'Thedan',
            'camera': '',
            'bio': '',
            'website': '',
            'phone': '',
            'location': '',
            'fee': '',
            'services': [],
            'photostyles': []
        }
        self.client.post(reverse_lazy('profile_edit'), data)
        updated_bob = User.objects.first()
        self.assertEqual(updated_bob.email, 'test@yahoo.com')
        self.assertEqual(updated_bob.first_name, 'Man')
        self.assertEqual(updated_bob.last_name, 'Thedan')

    def test_profile_edit_route_post_logged_in_done_redirects_to_profile(self):
        """Test post to profile edit route when logged in redirects to profile when done."""
        self.client.login(username='bob', password='password')
        data = {
            'email': 'notatest@gmail.com',
            'first_name': '',
            'last_name': '',
        }
        response = self.client.post(reverse_lazy('profile_edit'), data, follow=True)
        self.assertIn(b'Edit Profile\n    </a>', response.content)

    def test_profile_edit_route_post_logged_in_bad_data_has_200(self):
        """Test that profile edit route post with bad data has 200 code."""
        self.client.login(username='bob', password='password')
        data = {}
        response = self.client.post(reverse_lazy('profile_edit'), data)
        self.assertEqual(response.status_code, 200)

    def test_profile_edit_route_post_login_bad_data_has_error(self):
        """Test that album create route post with login has error."""
        self.client.login(username='bob', password='password')
        data = {}
        response = self.client.post(reverse_lazy('profile_edit'), data)
        self.assertIn(b'class="errorlist"', response.content)
