"""
KORNIALLE MODELS
================
These define the database tables. Each class = one table.

Frontend Dev Notes:
- Property = a hotel/cabin/villa listing shown on the site
- PropertyImage = photos for each property
- Pricing = per-night price, with optional date ranges for seasonal pricing
- Booking = when a guest reserves a property
- Review = guest reviews after a stay
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class PropertyType(models.TextChoices):
    HOTEL = 'hotel', '🏨 Hotel'
    VACATION_HOME = 'vacation_home', '🏠 Vacation Home'
    CABIN = 'cabin', '🏕️ Cabin'
    APARTMENT = 'apartment', '🏢 Apartment'


class Property(models.Model):
    """
    A stay listing — hotel, cabin, villa etc.
    Admins create these via /admin/ panel.
    """
    # Basic Info
    name = models.CharField(max_length=200, help_text="e.g. The Manhattan Suite Hotel")
    property_type = models.CharField(
        max_length=20, choices=PropertyType.choices, default=PropertyType.HOTEL
    )
    description = models.TextField(help_text="Full description shown on listing page")
    short_description = models.CharField(max_length=300, help_text="Short blurb for cards")

    # Location
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    address = models.CharField(max_length=300)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Main Photo
    main_image = models.ImageField(upload_to='properties/', blank=True, null=True)
    main_image_url = models.URLField(blank=True, help_text="Or use an external image URL")

    # Amenities (stored as checkboxes in admin)
    has_wifi = models.BooleanField(default=True, verbose_name="Free WiFi")
    has_pool = models.BooleanField(default=False, verbose_name="Pool")
    has_breakfast = models.BooleanField(default=False, verbose_name="Breakfast Included")
    has_free_cancellation = models.BooleanField(default=True, verbose_name="Free Cancellation")
    has_parking = models.BooleanField(default=False, verbose_name="Free Parking")
    has_gym = models.BooleanField(default=False, verbose_name="Gym")
    has_hot_tub = models.BooleanField(default=False, verbose_name="Hot Tub")
    has_fire_pit = models.BooleanField(default=False, verbose_name="Fire Pit")
    has_ocean_view = models.BooleanField(default=False, verbose_name="Ocean View")
    has_city_view = models.BooleanField(default=False, verbose_name="City View")

    # Capacity
    max_guests = models.PositiveIntegerField(default=2)
    max_rooms = models.PositiveIntegerField(default=1)

    # Status
    is_active = models.BooleanField(default=True, help_text="Uncheck to hide from site")
    is_featured = models.BooleanField(default=False, help_text="Show in featured section")
    is_deal = models.BooleanField(default=False, help_text="Show in deals section")

    # Rating (auto-calculated from reviews but can be set manually)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    review_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Properties"
        ordering = ['-is_featured', '-rating']

    def __str__(self):
        return f"{self.name} — {self.city}, {self.state}"

    def get_image(self):
        """Returns the best available image URL"""
        if self.main_image:
            return self.main_image.url
        return self.main_image_url or '/static/css/placeholder.jpg'

    def get_amenities(self):
        """Returns list of enabled amenities for template display"""
        amenities = []
        if self.has_wifi: amenities.append("Free WiFi")
        if self.has_pool: amenities.append("Pool")
        if self.has_breakfast: amenities.append("Breakfast")
        if self.has_free_cancellation: amenities.append("Free cancellation")
        if self.has_parking: amenities.append("Free Parking")
        if self.has_gym: amenities.append("Gym")
        if self.has_hot_tub: amenities.append("Hot tub")
        if self.has_fire_pit: amenities.append("Fire pit")
        if self.has_ocean_view: amenities.append("Ocean view")
        if self.has_city_view: amenities.append("City view")
        return amenities

    def get_current_price(self):
        """Get the current active price for this property"""
        pricing = self.pricing_set.filter(is_active=True).first()
        return pricing if pricing else None


class PropertyImage(models.Model):
    """Additional photos for a property"""
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='properties/gallery/')
    image_url = models.URLField(blank=True)
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Image for {self.property.name}"


class Pricing(models.Model):
    """
    Pricing for a property.
    Admins can set the nightly rate and optional discounts.
    Multiple pricing entries allow seasonal pricing.
    """
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default="Standard Rate",
                           help_text="e.g. 'Standard Rate', 'Summer Special', 'Weekend Rate'")

    # Pricing
    price_per_night = models.DecimalField(max_digits=8, decimal_places=2,
                                          validators=[MinValueValidator(0)])
    original_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True,
                                         help_text="If set, shows as strikethrough (sale price)")
    discount_percent = models.PositiveIntegerField(default=0,
                                                    help_text="e.g. 18 = 18% off badge shown")

    # Date range for seasonal pricing (optional)
    valid_from = models.DateField(null=True, blank=True)
    valid_to = models.DateField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_active', 'price_per_night']

    def __str__(self):
        return f"{self.property.name} — ${self.price_per_night}/night ({self.name})"


class Booking(models.Model):
    """
    A reservation made by a guest.
    Created when the booking form is submitted.
    """
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELLED = 'cancelled', 'Cancelled'
        COMPLETED = 'completed', 'Completed'

    class PaymentMethod(models.TextChoices):
        STRIPE = 'stripe', 'Stripe'
        CARD = 'card', 'Credit/Debit Card'
        PAYPAL = 'paypal', 'PayPal'

    # Guest — linked to user account if logged in
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)

    # Stay details
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    adults = models.PositiveIntegerField(default=1)
    children = models.PositiveIntegerField(default=0)
    rooms = models.PositiveIntegerField(default=1)
    special_requests = models.TextField(blank=True)

    # Payment
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices,
                                       default=PaymentMethod.STRIPE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Status
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    confirmation_code = models.CharField(max_length=20, unique=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking #{self.confirmation_code} — {self.first_name} {self.last_name} @ {self.property.name}"

    def nights(self):
        return (self.check_out - self.check_in).days

    def save(self, *args, **kwargs):
        # Auto-generate confirmation code
        if not self.confirmation_code:
            import random, string
            self.confirmation_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

        # Auto-calculate total price
        if not self.total_price and self.check_in and self.check_out:
            pricing = self.property.get_current_price()
            if pricing:
                nights = self.nights()
                self.total_price = pricing.price_per_night * nights * self.rooms

        super().save(*args, **kwargs)


class Review(models.Model):
    """
    Guest review for a property.
    Only guests with a completed booking can leave reviews (enforced in views).
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='reviews')
    booking = models.OneToOneField(Booking, on_delete=models.SET_NULL, null=True, blank=True)

    reviewer_name = models.CharField(max_length=100)
    reviewer_location = models.CharField(max_length=100, blank=True,
                                          help_text="e.g. 'New York City · Jan 2026'")
    rating = models.DecimalField(max_digits=3, decimal_places=1,
                                  validators=[MinValueValidator(0), MaxValueValidator(10)])
    review_text = models.TextField()
    is_verified = models.BooleanField(default=False, help_text="Mark as verified stay")
    is_approved = models.BooleanField(default=False, help_text="Approve to show on site")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reviewer_name} — {self.property.name} ({self.rating}/10)"


class UserProfile(models.Model):
    """
    Extended profile for registered users.
    Automatically created when a user registers.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=30, blank=True)
    newsletter = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile: {self.user.username}"
