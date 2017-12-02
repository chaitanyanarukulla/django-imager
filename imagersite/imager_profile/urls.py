"""."""
from django.conf.urls import url
from imager_profile.views import profile_view

urlpatterns = [
    url(r'(?P<username>.*)$', profile_view, name='profile')
]
