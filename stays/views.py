"""
KORNIALLE VIEWS
================
Views receive HTTP requests and return HTML responses.
Each view is a Python function (or class) that:
1. Gets data from the database
2. Passes it to a template
3. Returns the rendered HTML to the browser

Frontend Dev Notes:
- Each view corresponds to a URL and a template file
- Data passed via 'context' dict is available in templates as {{ variable_name }}
- Form submissions hit these views via POST requests
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q

from .models import Property, Pricing, Booking, Review, UserProfile
from .forms import BookingForm, ReviewForm, RegisterForm, LoginForm


# ─────────────────────────────────────────
# HOME / INDEX VIEW
# ─────────────────────────────────────────

def home(request):
    """
    Main homepage — /
    Renders the full Kornialle homepage with all sections.
    """
    # Get data for the page
    featured_properties = Property.objects.filter(is_active=True, is_featured=True)[:4]
    all_properties = Property.objects.filter(is_active=True)
    deal_properties = Property.objects.filter(is_active=True, is_deal=True)[:3]
    approved_reviews = Review.objects.filter(is_approved=True)[:6]

    # Get distinct cities for the "Popular Destinations" section
    cities = Property.objects.filter(is_active=True).values_list(
        'city', 'state'
    ).distinct()[:6]

    # Property type filter
    prop_type = request.GET.get('type', '')
    if prop_type:
        all_properties = all_properties.filter(property_type=prop_type)

    # Search
    search_q = request.GET.get('q', '')
    if search_q:
        all_properties = all_properties.filter(
            Q(city__icontains=search_q) |
            Q(state__icontains=search_q) |
            Q(name__icontains=search_q)
        )

    # Booking form (shown in the "Make a Booking" section)
    booking_form = BookingForm()

    # Review form (shown at the bottom reviews section)
    review_form = ReviewForm()

    context = {
        'featured_properties': featured_properties,
        'all_properties': all_properties,
        'deal_properties': deal_properties,
        'approved_reviews': approved_reviews,
        'cities': cities,
        'booking_form': booking_form,
        'review_form': review_form,
        'search_q': search_q,
        'prop_type': prop_type,
    }
    return render(request, 'stays/home.html', context)


# ─────────────────────────────────────────
# PROPERTY DETAIL VIEW
# ─────────────────────────────────────────

def property_detail(request, pk):
    """
    Individual property page — /property/<pk>/
    Shows full details, pricing, photos, and reviews for one property.
    """
    property = get_object_or_404(Property, pk=pk, is_active=True)
    pricing = property.get_current_price()
    images = property.images.all()
    reviews = property.reviews.filter(is_approved=True)
    booking_form = BookingForm(initial={'property': property})

    context = {
        'property': property,
        'pricing': pricing,
        'images': images,
        'reviews': reviews,
        'booking_form': booking_form,
        'amenities': property.get_amenities(),
    }
    return render(request, 'stays/property_detail.html', context)


# ─────────────────────────────────────────
# BOOKING VIEWS
# ─────────────────────────────────────────

def make_booking(request):
    """
    Handles the booking form POST submission — /booking/
    Frontend sends form data here via POST.
    """
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)

            # Link to logged-in user if available
            if request.user.is_authenticated:
                booking.user = request.user

            booking.save()

            # Send confirmation email (if configured)
            # from django.core.mail import send_mail
            # send_mail(...)

            messages.success(
                request,
                f"🎉 Booking confirmed! Your confirmation code is {booking.confirmation_code}"
            )
            return redirect('booking_confirmation', code=booking.confirmation_code)
        else:
            messages.error(request, "Please fix the errors below.")

    # If GET or invalid form, redirect home
    return redirect('home')


def booking_confirmation(request, code):
    """Shows booking confirmation page — /booking/confirmation/<code>/"""
    booking = get_object_or_404(Booking, confirmation_code=code)
    return render(request, 'stays/booking_confirmation.html', {'booking': booking})


@login_required
def my_bookings(request):
    """User's booking history — /my-bookings/ (requires login)"""
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'stays/my_bookings.html', {'bookings': bookings})


# ─────────────────────────────────────────
# REVIEW VIEWS
# ─────────────────────────────────────────

def submit_review(request):
    """Handles review form POST — /reviews/submit/"""
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            if request.user.is_authenticated:
                review.user = request.user
                review.is_verified = True  # Auto-verify logged-in users
            review.save()
            messages.success(request, "✅ Thank you! Your review is pending approval.")
        else:
            messages.error(request, "Please fill in all review fields correctly.")
    return redirect('home')


# ─────────────────────────────────────────
# AUTH VIEWS
# ─────────────────────────────────────────

def register_view(request):
    """
    Registration page — /auth/register/
    Shows registration form and handles new user creation.
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto-login after registration
            messages.success(request, f"Welcome to Kornialle, {user.first_name}! 🎉")
            return redirect('home')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = RegisterForm()

    return render(request, 'stays/register.html', {'form': form})


def login_view(request):
    """
    Login page — /auth/login/
    Handles username/password authentication.
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Allow login with email too
            if '@' in username:
                from django.contrib.auth.models import User as AuthUser
                try:
                    user_obj = AuthUser.objects.get(email=username)
                    username = user_obj.username
                except AuthUser.DoesNotExist:
                    pass

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if not form.cleaned_data.get('remember_me'):
                    request.session.set_expiry(0)  # Session expires on browser close
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Please fill in all fields.")
    else:
        form = LoginForm()

    return render(request, 'stays/login.html', {'form': form})


def logout_view(request):
    """Logs out the user — /auth/logout/"""
    logout(request)
    messages.info(request, "You've been signed out. See you soon!")
    return redirect('home')


@login_required
def profile_view(request):
    """User profile/account page — /profile/"""
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)

    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')[:5]

    return render(request, 'stays/profile.html', {
        'profile': profile,
        'bookings': bookings,
    })


# ─────────────────────────────────────────
# SEARCH / FILTER API (for JS fetch calls)
# ─────────────────────────────────────────

def search_properties(request):
    """
    JSON endpoint for property search — /api/search/
    Frontend JS can call this to filter properties without page reload.
    Returns: [{ id, name, city, state, price, image, rating }, ...]
    """
    q = request.GET.get('q', '')
    prop_type = request.GET.get('type', '')
    city = request.GET.get('city', '')

    properties = Property.objects.filter(is_active=True)

    if q:
        properties = properties.filter(
            Q(name__icontains=q) | Q(city__icontains=q) | Q(state__icontains=q)
        )
    if prop_type:
        properties = properties.filter(property_type=prop_type)
    if city:
        properties = properties.filter(city__icontains=city)

    results = []
    for p in properties[:20]:
        pricing = p.get_current_price()
        results.append({
            'id': p.id,
            'name': p.name,
            'city': p.city,
            'state': p.state,
            'type': p.get_property_type_display(),
            'price': str(pricing.price_per_night) if pricing else None,
            'original_price': str(pricing.original_price) if pricing and pricing.original_price else None,
            'discount': pricing.discount_percent if pricing else 0,
            'image': p.get_image(),
            'rating': str(p.rating),
            'review_count': p.review_count,
            'amenities': p.get_amenities(),
        })

    return JsonResponse({'results': results, 'count': len(results)})
