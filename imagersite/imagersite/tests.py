"""Tests for the imagersite routes."""
from django.test import TestCase
from imager_profile.models import User


class RoutingTests(TestCase):
    """Tests for the routes in imagersite."""

    def setUp(self):
        """Set up a user for testing login.."""
        user = User(username='bob', email='bob@bob.net')
        user.set_password('password')
        user.save()

    def test_home_route_has_200_response(self):
        """Test that home route has a 200 response code."""
        response = self.client.get('/')
        self.assertEquals(response.status_code, 200)

    def test_home_route_has_gallery(self):
        """Test that home route has a gallery on the page."""
        response = self.client.get('/')
        self.assertIn(b'tz-gallery', response.content)

    def test_login_get_has_200_response(self):
        """Test that login get route has a 200 response code."""
        response = self.client.get('/login/')
        self.assertEquals(response.status_code, 200)

    def test_login_get_login_form(self):
        """Test that login get route has a login form."""
        response = self.client.get('/login/')
        self.assertIn(b'<h2 class="title">Login</h2>', response.content)

    def test_login_post_invalid_user_has_200_response(self):
        """Test that login with invalid username has a 200 response code."""
        response = self.client.post('/login/', {
            'username': 'fred',
            'password': 'password'
        })
        self.assertEquals(response.status_code, 200)

    def test_login_post_invalid_user_displays_invalid_login(self):
        """Test that login with invalid username displays to bad login."""
        response = self.client.post('/login/', {
            'username': 'fred',
            'password': 'password'
        })
        self.assertIn(b'Please try again.', response.content)

    def test_login_post_invalid_password_has_200_response(self):
        """Test that login with invalid username has a 200 response code."""
        response = self.client.post('/login/', {
            'username': 'bob',
            'password': 'passwordssss'
        })
        self.assertEquals(response.status_code, 200)

    def test_login_post_invalid_password_displays_invalid_login(self):
        """Test that login with invalid username displays to bad login."""
        response = self.client.post('/login/', {
            'username': 'bob',
            'password': 'passwordssss'
        })
        self.assertIn(b'Please try again.', response.content)

    def test_login_post_valid_login_has_302_response(self):
        """Test that login with valid login has a 302 response code."""
        response = self.client.post('/login/', {
            'username': 'bob',
            'password': 'password'
        })
        self.assertEquals(response.status_code, 302)

    def test_login_post_invalid_password_redirects_to_home_page(self):
        """Test that login with valid login redirects to home page."""
        response = self.client.get('/')
        self.assertNotIn(b'Welcome,', response.content)
        self.client.post('/login/', {
            'username': 'bob',
            'password': 'password'
        })
        response = self.client.get('/')
        self.assertIn(b'Welcome,', response.content)

    def test_logout_get_has_200_response(self):
        """Test that logout get route has a 200 response code."""
        response = self.client.get('/logout/')
        self.assertEquals(response.status_code, 200)

    def test_logout_get_has_logged_out_title(self):
        """Test that logout get route has logged-out title."""
        response = self.client.get('/logout/')
        self.assertIn(b'You Are Logged Out', response.content)

    def test_register_get_has_200_response(self):
        """Test that register get route has a 200 response code."""
        response = self.client.get('/accounts/register/')
        self.assertEquals(response.status_code, 200)

    def test_register_get_has_register_form(self):
        """Test that register get route has registration form."""
        response = self.client.get('/accounts/register/')
        self.assertIn(b'<h2 class="title">Register</h2>', response.content)
