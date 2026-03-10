"""
KORNIALLE URL PATTERNS
=======================
Maps URLs to view functions.

Frontend Dev Notes:
- {% url 'home' %}           → /
- {% url 'property_detail' pk=1 %} → /property/1/
- {% url 'make_booking' %}   → /booking/
- {% url 'login' %}          → /auth/login/
- {% url 'register' %}       → /auth/register/
- {% url 'logout' %}         → /auth/logout/
- {% url 'profile' %}        → /profile/
- {% url 'search_api' %}     → /api/search/
"""

from django.urls import path
from . import views

urlpatterns = [
    # Homepage
    path('', views.home, name='home'),

    # Properties
    path('property/<int:pk>/', views.property_detail, name='property_detail'),

    # Bookings
    path('booking/', views.make_booking, name='make_booking'),
    path('booking/confirmation/<str:code>/', views.booking_confirmation, name='booking_confirmation'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),

    # Reviews
    path('reviews/submit/', views.submit_review, name='submit_review'),

    # User profile
    path('profile/', views.profile_view, name='profile'),

    # Search API (called by JavaScript)
    path('api/search/', views.search_properties, name='search_api'),
]
