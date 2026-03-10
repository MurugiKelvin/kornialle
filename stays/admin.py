"""
KORNIALLE ADMIN CONFIGURATION
==============================
This controls the Django Admin panel at /admin/

Admins can:
- Add/Edit/Delete Properties with all details
- Set Pricing per property (nightly rates, discounts, seasonal pricing)
- View and manage Bookings
- Approve/reject Reviews
- Manage Users

Frontend Dev Notes:
- The admin panel is separate from the public site
- It lives at /admin/ and requires superuser login
- No frontend work needed here — Django generates this UI automatically
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Property, PropertyImage, Pricing, Booking, Review, UserProfile


class PropertyImageInline(admin.TabularInline):
    """Shows photo upload fields directly inside the Property admin page"""
    model = PropertyImage
    extra = 3
    fields = ['image', 'image_url', 'caption', 'order']


class PricingInline(admin.TabularInline):
    """Shows pricing fields directly inside the Property admin page"""
    model = Pricing
    extra = 1
    fields = ['name', 'price_per_night', 'original_price', 'discount_percent',
              'valid_from', 'valid_to', 'is_active']


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    """
    Full property management in admin.
    Admins can add properties with photos, amenities, and pricing all on one page.
    """
    list_display = [
        'name', 'property_type', 'city', 'state',
        'rating', 'review_count', 'is_active', 'is_featured', 'is_deal',
        'preview_image'
    ]
    list_filter = ['property_type', 'city', 'state', 'is_active', 'is_featured', 'is_deal']
    search_fields = ['name', 'city', 'state', 'description']
    list_editable = ['is_active', 'is_featured', 'is_deal']

    # Group fields into sections in the admin form
    fieldsets = (
        ('📍 Basic Information', {
            'fields': ('name', 'property_type', 'description', 'short_description')
        }),
        ('📌 Location', {
            'fields': ('address', 'city', 'state', 'latitude', 'longitude')
        }),
        ('🖼️ Main Image', {
            'fields': ('main_image', 'main_image_url'),
            'description': 'Upload a photo OR paste an image URL'
        }),
        ('🏊 Amenities', {
            'fields': (
                ('has_wifi', 'has_pool', 'has_breakfast', 'has_free_cancellation'),
                ('has_parking', 'has_gym', 'has_hot_tub', 'has_fire_pit'),
                ('has_ocean_view', 'has_city_view'),
            ),
            'classes': ('collapse',),
        }),
        ('👥 Capacity', {
            'fields': ('max_guests', 'max_rooms')
        }),
        ('⭐ Ratings', {
            'fields': ('rating', 'review_count')
        }),
        ('🔧 Visibility', {
            'fields': ('is_active', 'is_featured', 'is_deal')
        }),
    )

    inlines = [PricingInline, PropertyImageInline]

    def preview_image(self, obj):
        url = obj.get_image()
        if url and url != '/static/css/placeholder.jpg':
            return format_html('<img src="{}" style="height:40px;border-radius:4px;">', url)
        return '—'
    preview_image.short_description = 'Photo'


@admin.register(Pricing)
class PricingAdmin(admin.ModelAdmin):
    """
    Standalone pricing management.
    Admins can also manage all prices from here, or from inside the Property page.
    """
    list_display = ['property', 'name', 'price_per_night', 'original_price',
                    'discount_percent', 'valid_from', 'valid_to', 'is_active']
    list_filter = ['is_active', 'property__city']
    search_fields = ['property__name', 'name']
    list_editable = ['price_per_night', 'is_active']

    fieldsets = (
        ('Property', {
            'fields': ('property', 'name')
        }),
        ('💰 Pricing', {
            'fields': ('price_per_night', 'original_price', 'discount_percent'),
            'description': 'Set original_price to show a strikethrough "was" price'
        }),
        ('📅 Seasonal Dates (Optional)', {
            'fields': ('valid_from', 'valid_to'),
            'description': 'Leave blank for year-round pricing',
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """View and manage all bookings"""
    list_display = [
        'confirmation_code', 'first_name', 'last_name', 'email',
        'property', 'check_in', 'check_out', 'nights_display',
        'total_price', 'status', 'created_at'
    ]
    list_filter = ['status', 'payment_method', 'property', 'check_in']
    search_fields = ['confirmation_code', 'first_name', 'last_name', 'email']
    list_editable = ['status']
    readonly_fields = ['confirmation_code', 'created_at', 'total_price']

    fieldsets = (
        ('🔖 Booking Info', {
            'fields': ('confirmation_code', 'status', 'created_at')
        }),
        ('👤 Guest Details', {
            'fields': ('user', 'first_name', 'last_name', 'email', 'phone')
        }),
        ('🏨 Stay Details', {
            'fields': ('property', 'check_in', 'check_out', 'adults', 'children', 'rooms', 'special_requests')
        }),
        ('💳 Payment', {
            'fields': ('payment_method', 'total_price')
        }),
    )

    def nights_display(self, obj):
        return f"{obj.nights()} nights"
    nights_display.short_description = "Nights"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Approve or reject guest reviews"""
    list_display = ['reviewer_name', 'property', 'rating', 'is_verified', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'is_verified', 'property']
    search_fields = ['reviewer_name', 'review_text', 'property__name']
    list_editable = ['is_approved', 'is_verified']

    actions = ['approve_reviews', 'reject_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f"{queryset.count()} review(s) approved.")
    approve_reviews.short_description = "✅ Approve selected reviews"

    def reject_reviews(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, f"{queryset.count()} review(s) rejected.")
    reject_reviews.short_description = "❌ Reject selected reviews"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'newsletter', 'created_at']
    search_fields = ['user__username', 'user__email']
