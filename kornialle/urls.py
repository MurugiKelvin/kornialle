from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django Admin Panel — accessible at /admin/
    # This is where admins add/edit/delete properties and prices
    path('admin/', admin.site.urls),

    # Main stays app URLs
    path('', include('stays.urls')),

    # Authentication URLs (login, logout, register)
    path('auth/', include('stays.auth_urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Customize admin panel branding
admin.site.site_header = "Kornialle Admin"
admin.site.site_title = "Kornialle Management"
admin.site.index_title = "Welcome to Kornialle Admin Panel"
