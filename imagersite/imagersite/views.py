"""."""
from django.shortcuts import render


def home_view(request):
    """Get the Home page."""
    return render(request, 'imagersite/home.html')
