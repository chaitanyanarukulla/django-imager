"""View functions for the profile page."""
from django.shortcuts import render


def profile_view(request, username=None):
    """Render the profile for a user."""
    context = {
        'username': 'bob',
        'bio': 'hello, i am bob. bob bob bob bob bob bob bob bob bob bob bob bob bob bob bob bob bob bob bob bob bob bob bob bob bob bob bob bob bob bob bob bob bob bob bob bob bob bob bob bob bob bob bob bob.',
        'camera': 'Mirrorless',
        'email': 'bob@bob.com',
        'website': 'www.bob.com',
        'fee': "{:,.2f}".format(1000000.00),
        'location': 'here',
        'phone': '123-4567',
        'services': ['weddings', 'babies'],
        'photostyles': ['night'],
        'albums': ['album', 'album', 'album', 'album', 'album', 'album', 'album', 'album', 'album', 'album', 'album', 'album', 'album', 'album', 'album', 'album', 'album', 'album', 'album', 'album', 'album', 'album', 'album', 'album'],
        'photos': [],
    }
    return render(request, 'imager_profile/profile.html', context)
