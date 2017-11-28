"""Tests for the imagersite routes."""
from django.test import TestCase
from imager_profile.models import User
from django.core import mail


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
        self.assertEqual(response.status_code, 200)

    def test_home_route_has_gallery(self):
        """Test that home route has a gallery on the page."""
        response = self.client.get('/')
        self.assertIn(b'tz-gallery', response.content)

    def test_login_get_has_200_response(self):
        """Test that login get route has a 200 response code."""
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)

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
        self.assertEqual(response.status_code, 200)

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
        self.assertEqual(response.status_code, 200)

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
        self.assertEqual(response.status_code, 302)

    def test_login_post_validates_users(self):
        """Test that login validates users."""
        response = self.client.get('/')
        self.assertNotIn(b'Welcome,', response.content)
        self.client.post('/login/', {
            'username': 'bob',
            'password': 'password'
        })
        response = self.client.get('/')
        self.assertIn(b'Welcome,', response.content)

    def test_login_post_valid_login_redirects_to_home_page(self):
        """Test that login with valid login redirects to home page."""
        response = self.client.post('/login/', {
            'username': 'bob',
            'password': 'password'
        }, follow=True)
        self.assertEqual(response.redirect_chain[0][0], '/')

    def test_logout_get_has_200_response(self):
        """Test that logout get route has a 200 response code."""
        response = self.client.get('/logout/')
        self.assertEqual(response.status_code, 200)

    def test_logout_get_has_logged_out_title(self):
        """Test that logout get route has logged-out title."""
        response = self.client.get('/logout/')
        self.assertIn(b'You Are Logged Out', response.content)

    def test_logout_from_login_user_will_logsout_user(self):
        """Test that logout will redirects to logout page."""
        self.client.login(username='bob', password='password')
        response = self.client.get('/')
        self.assertIn(b'Welcome,', response.content)
        self.client.get('/logout/')
        response = self.client.get('/')
        self.assertNotIn(b'Welcome,', response.content)

    def test_register_get_has_200_response(self):
        """Test that register get route has a 200 response code."""
        response = self.client.get('/accounts/register/')
        self.assertEqual(response.status_code, 200)

    def test_register_get_has_register_form(self):
        """Test that register get route has registration form."""
        response = self.client.get('/accounts/register/')
        self.assertIn(b'<h2 class="title">Register</h2>', response.content)

    def test_register_will_send_email_after_registration(self):
        """Test registration will send Email after Registartion."""
        self.client.post('/accounts/register/', {
            'username': 'Rob',
            'password1': 'Codefellows',
            'password2': 'Codefellows',
            'email': 'rob@email.com'
        })
        self.assertEqual(len(mail.outbox), 1)

    def test_register_redirects_to_registration_complete_page(self):
        """Test register redirects to registration complate page."""
        response = self.client.post('/accounts/register/', {
            'username': 'Rob',
            'password1': 'Codefellows',
            'password2': 'Codefellows',
            'email': 'rob@email.com'
        }, follow=True)
        self.assertIn(b'Registration is Compleated', response.content)

    def test_register_valid_user_password_gets_302_response(self):
        """Test if valid user with password responds with 302."""
        response = self.client.post('/accounts/register/', {
            'username': 'Rob',
            'password1': 'Codefellows',
            'password2': 'Codefellows',
            'email': 'rob@email.com'
        })
        self.assertEqual(response.status_code, 302)

    def test_register_will_send_email_and_link_after_registration(self):
        """Test registration will send Email and link after Registartion."""
        self.client.post('/accounts/register/', {
            'username': 'Rob',
            'password1': 'Codefellows',
            'password2': 'Codefellows',
            'email': 'rob@email.com'
        })
        self.assertIn('/accounts/activate/', mail.outbox[0].body)

    def test_actvation_link_redirects_to_activate_complated_page(self):
        """Test if Acitvation link works."""
        import re
        self.client.post('/accounts/register/', {
            'username': 'Rob',
            'password1': 'Codefellows',
            'password2': 'Codefellows',
            'email': 'rob@email.com'
        })
        activation = re.findall('/accounts/activate/.+/', mail.outbox[0].body)
        response = self.client.get(activation[0], follow=True)
        self.assertIn(b'Activation is Compleated', response.content)

    def test_register_allows_login_to_new_users(self):
        """Test if users created can log in."""
        import re
        self.client.login(username='Rob', password='Codefellows')
        response = self.client.get('/')
        self.assertNotIn(b'Welcome,', response.content)
        self.client.post('/accounts/register/', {
            'username': 'Rob',
            'password1': 'Codefellows',
            'password2': 'Codefellows',
            'email': 'rob@email.com'
        })
        activation = re.findall('/accounts/activate/.+/', mail.outbox[0].body)
        self.client.get(activation[0])
        self.client.login(username='Rob', password='Codefellows')
        response = self.client.get('/')
        self.assertIn(b'Welcome,', response.content)

    def test_register_taken_username_responds_with_200(self):
        """Test register taken responds with 200."""
        response = self.client.post('/accounts/register/', {
            'username': 'bob',
            'password1': 'Codefellows',
            'password2': 'Codefellows',
            'email': 'bob@email.com'
        })
        self.assertEqual(200, response.status_code)

    def test_register_taken_user_name_displays_name_taken(self):
        """Test register taken responds with username taken."""
        response = self.client.post('/accounts/register/', {
            'username': 'bob',
            'password1': 'Codefellows',
            'password2': 'Codefellows',
            'email': 'bob@email.com'
        })
        self.assertIn(b'username already exists', response.content)
