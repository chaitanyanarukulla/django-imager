"""."""
from django.shortcuts import render


def home_view(request):
    """."""
    return render(request, 'imagersite/home.html')


def register_view(request):
    """."""
    return render(request, 'imagersite/register.html')
