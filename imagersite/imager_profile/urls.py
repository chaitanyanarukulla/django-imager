"""."""
from django.conf.urls import url
from imager_profile.views import ProfileView

urlpatterns = [
    url(r'(?P<username>.*)$', ProfileView.as_view(), name='profile')
]
