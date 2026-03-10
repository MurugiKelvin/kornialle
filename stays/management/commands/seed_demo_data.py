"""
Management command to seed demo data.
Run: python manage.py seed_demo_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from stays.models import Property, PriceRule, Review, UserProfile


PROPERTIES = [
    {
        'name': 'The Manhattan Suite Hotel',
        'property_type': 'hotel',
        'city': 'New York City',
        'state': 'NY',
        'address': '123 Fifth Avenue, Manhattan, New York, NY 10001',
        'description': 'A luxurious boutique hotel in the heart of Manhattan with stunning skyline views, world-class dining, and impeccable service.',
        'image_url': 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=600&auto=format&fit=crop&q=75',
        'amenities': 'Free WiFi, Breakfast, Free cancellation, Rooftop bar, 24hr concierge',
        'is_featured': True,
        'prices': [
            {'season': 'standard', 'price': 340, 'discount': 18},
            {'season': 'weekend', 'price': 420, 'discount': 0},
            {'season': 'peak', 'price': 480, 'discount': 0},
        ],
    },
    {
        'name': 'Ocean View Luxury Villa',
        'property_type': 'vacation_home',
        'city': 'Miami Beach',
        'state': 'FL',
        'address': '88 Ocean Drive, Miami Beach, FL 33139',
        'description': 'A breathtaking oceanfront villa with private pool, direct beach access, and panoramic Atlantic views from every room.',
        'image_url': 'https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=600&auto=format&fit=crop&q=75',
        'amenities': 'Private Pool, Ocean View, Free cancellation, Beach access, Full kitchen',
        'is_featured': True,
        'prices': [
            {'season': 'standard', 'price': 420, 'discount': 0},
            {'season': 'peak', 'price': 580, 'discount': 0},
        ],
    },
    {
        'name': 'Smoky Mountain Forest Cabin',
        'property_type': 'cabin',
        'city': 'Asheville',
        'state': 'NC',
        'address': '12 Blue Ridge Pkwy, Asheville, NC 28801',
        'description': 'Escape to this magical mountain cabin surrounded by ancient forest. Features a hot tub, fire pit, and stunning Smoky Mountain vistas.',
        'image_url': 'https://images.unsplash.com/photo-1588880331179-bc9b93a8cb5e?w=600&auto=format&fit=crop&q=75',
        'amenities': 'Hot tub, Fire pit, Free cancellation, Mountain views, Hiking trails',
        'is_featured': True,
        'prices': [
            {'season': 'standard', 'price': 195, 'discount': 24},
            {'season': 'weekend', 'price': 220, 'discount': 10},
        ],
    },
    {
        'name': 'Riverwalk Boutique Loft',
        'property_type': 'apartment',
        'city': 'Chicago',
        'state': 'IL',
        'address': '420 N Michigan Ave, Chicago, IL 60611',
        'description': 'A sleek modern loft steps from the Chicago Riverwalk, Millennium Park, and the best dining in the city.',
        'image_url': 'https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=600&auto=format&fit=crop&q=75',
        'amenities': 'City view, Gym, Free cancellation, Concierge, Rooftop access',
        'is_featured': True,
        'prices': [
            {'season': 'standard', 'price': 210, 'discount': 0},
            {'season': 'off_peak', 'price': 170, 'discount': 0},
        ],
    },
    {
        'name': 'Nashville Music Row Suites',
        'property_type': 'hotel',
        'city': 'Nashville',
        'state': 'TN',
        'address': '16th Ave S, Nashville, TN 37212',
        'description': 'Stylish suites in the heart of Music Row, walking distance to Broadway honky-tonks, world-class BBQ, and live music every night.',
        'image_url': 'https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?w=600&auto=format&fit=crop&q=75',
        'amenities': 'Rooftop pool, Free WiFi, Live music lounge, Free breakfast',
        'is_featured': False,
        'prices': [
            {'season': 'standard', 'price': 180, 'discount': 0},
            {'season': 'weekend', 'price': 240, 'discount': 0},
        ],
    },
]

REVIEWS = [
    ('The Manhattan Suite Hotel', 'Sarah M.', 'New York City, NY', 9.5, 'Absolutely flawless from booking to check-out. The property was even better than the photos — will definitely be back.'),
    ('Ocean View Luxury Villa', 'James & Priya', 'Miami Beach, FL', 9.8, 'Incredible service, great deal, and the ocean views were breathtaking. Kornialle made everything so effortless.'),
    ('Riverwalk Boutique Loft', 'Maria L.', 'Chicago, IL', 9.2, 'Easy checkout, seamless check-in and the staff were so welcoming. Highly recommend to anyone visiting the US.'),
]


class Command(BaseCommand):
    help = 'Seeds the database with demo properties, prices, and reviews'

    def handle(self, *args, **kwargs):
        self.stdout.write('🌱 Seeding demo data...')

        # Create superuser if needed
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser('admin', 'admin@kornialle.com', 'admin1234')
            UserProfile.objects.get_or_create(user=admin)
            self.stdout.write(self.style.SUCCESS('✅ Created superuser: admin / admin1234'))

        # Seed properties
        for data in PROPERTIES:
            prices = data.pop('prices')
            prop, created = Property.objects.get_or_create(name=data['name'], defaults=data)
            if created:
                self.stdout.write(f'  🏨 Created: {prop.name}')
                for p in prices:
                    PriceRule.objects.create(
                        property=prop,
                        season=p['season'],
                        price_per_night=p['price'],
                        discount_percent=p['discount'],
                        is_active=True,
                    )
            else:
                self.stdout.write(f'  ↩️  Skipped (exists): {prop.name}')
            data['prices'] = prices  # restore for loop safety

        # Seed reviews
        for prop_name, name, location, rating, comment in REVIEWS:
            try:
                prop = Property.objects.get(name=prop_name)
                if not prop.reviews.filter(reviewer_name=name).exists():
                    Review.objects.create(
                        property=prop,
                        reviewer_name=name,
                        reviewer_location=location,
                        rating=rating,
                        comment=comment,
                        is_verified=True,
                    )
                    self.stdout.write(f'  ⭐ Review by {name}')
            except Property.DoesNotExist:
                pass

        self.stdout.write(self.style.SUCCESS('\n✅ Demo data seeded successfully!'))
        self.stdout.write('👉 Run: python manage.py runserver')
        self.stdout.write('👉 Admin at: http://127.0.0.1:8000/admin/')
        self.stdout.write('👉 Login: admin / admin1234')
