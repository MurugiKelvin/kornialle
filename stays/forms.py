"""
KORNIALLE FORMS
================
Forms handle user input validation before saving to database.

Frontend Dev Notes:
- Each form maps to an HTML <form> on the site
- {{ form.field_name }} renders the input field in templates
- {{ form.errors }} shows validation errors
- Always include {% csrf_token %} inside <form> tags
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Booking, Review, UserProfile


class RegisterForm(UserCreationForm):
    """
    Registration form — used on the /auth/register/ page.
    Extends Django's built-in UserCreationForm to add email field.
    """
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-input',
        'placeholder': 'your@email.com'
    }))
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'First name'
    }))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'Last name'
    }))
    phone = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': '+1 (555) 000-0000'
    }))
    newsletter = forms.BooleanField(required=False, label="Send me deals and offers by email")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not field.widget.attrs.get('class'):
                field.widget.attrs['class'] = 'form-input'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            # Create user profile
            UserProfile.objects.create(
                user=user,
                phone=self.cleaned_data.get('phone', ''),
                newsletter=self.cleaned_data.get('newsletter', False)
            )
        return user


class LoginForm(forms.Form):
    """Login form — used on /auth/login/ page"""
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'Username or email',
        'autofocus': True
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input',
        'placeholder': 'Password'
    }))
    remember_me = forms.BooleanField(required=False, label="Remember me")


class BookingForm(forms.ModelForm):
    """
    Booking form — used in the booking section on the homepage.
    Maps directly to the existing HTML booking form.
    """
    class Meta:
        model = Booking
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'property', 'check_in', 'check_out',
            'adults', 'children', 'rooms',
            'special_requests', 'payment_method'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Phone'}),
            'property': forms.Select(attrs={'class': 'form-select'}),
            'check_in': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'check_out': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'adults': forms.NumberInput(attrs={'class': 'form-input', 'min': 1}),
            'children': forms.NumberInput(attrs={'class': 'form-input', 'min': 0}),
            'rooms': forms.NumberInput(attrs={'class': 'form-input', 'min': 1}),
            'special_requests': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
            'payment_method': forms.RadioSelect(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active properties in the dropdown
        from .models import Property
        self.fields['property'].queryset = Property.objects.filter(is_active=True)

    def clean(self):
        cleaned = super().clean()
        check_in = cleaned.get('check_in')
        check_out = cleaned.get('check_out')
        if check_in and check_out:
            if check_out <= check_in:
                raise forms.ValidationError("Check-out must be after check-in.")
        return cleaned


class ReviewForm(forms.ModelForm):
    """Review submission form — maps to the review form at the bottom of the site"""
    class Meta:
        model = Review
        fields = ['reviewer_name', 'property', 'rating', 'review_text']
        widgets = {
            'reviewer_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Your Name'}),
            'property': forms.Select(attrs={'class': 'form-select'}),
            'rating': forms.NumberInput(attrs={
                'class': 'form-input', 'min': '0', 'max': '10', 'step': '0.1'
            }),
            'review_text': forms.Textarea(attrs={
                'class': 'form-textarea', 'rows': 4,
                'placeholder': 'Share your experience...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Property
        self.fields['property'].queryset = Property.objects.filter(is_active=True)
