"""."""
from django.conf.urls import url
from imager_profile.views import ProfileView, ProfileEditView

urlpatterns = [
    url(r'^edit$', ProfileEditView.as_view(), name='profile_edit'),
    url(r'^(?P<username>.*)$', ProfileView.as_view(), name='profile')
]
