from django import forms
from django.core.validators import validate_email, MinLengthValidator, MaxLengthValidator
from django.utils.html import escape
from .models import SecureUser
import re

class SecureUserForm(forms.ModelForm):
    """
    Secure form for user data with comprehensive validation and sanitization.
    Implements protection against SQL injection and XSS attacks.
    """
    
    class Meta:
        model = SecureUser
        fields = ['name', 'email', 'bio']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about yourself...',
                'maxlength': '500'
            }),
        }
    
    def clean_name(self):
        """
        Validate and sanitize name field.
        Prevents SQL injection and XSS by removing dangerous characters.
        """
        name = self.cleaned_data['name']
        
        # Remove potentially dangerous characters
        name = re.sub(r'[<>&\"\';]', '', name)
        
        # Validate length
        if len(name) < 2:
            raise forms.ValidationError("Name must be at least 2 characters long.")
        
        if len(name) > 100:
            raise forms.ValidationError("Name must not exceed 100 characters.")
        
        # Escape any remaining HTML to prevent XSS
        return escape(name)
    
    def clean_email(self):
        """
        Validate email using Django's built-in validator and additional checks.
        """
        email = self.cleaned_data['email']
        
        # Django's built-in email validation
        validate_email(email)
        
        # Additional custom validation
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise forms.ValidationError("Please enter a valid email address.")
        
        return email.lower()  # Normalize email to lowercase
    
    def clean_bio(self):
        """
        Sanitize bio field to allow safe HTML while preventing XSS.
        """
        bio = self.cleaned_data['bio']
        
        if not bio:
            return bio
        
        # Remove script tags and event handlers to prevent XSS
        bio = re.sub(r'<script.*?</script>', '', bio, flags=re.IGNORECASE | re.DOTALL)
        bio = re.sub(r'on\w+=\s*[\'\"].*?[\'\"]', '', bio, flags=re.IGNORECASE)
        
        # Escape any remaining HTML tags
        bio = escape(bio)
        
        # Validate length
        if len(bio) > 500:
            raise forms.ValidationError("Bio must not exceed 500 characters.")
        
        return bio

class SearchForm(forms.Form):
    """
    Secure search form with input validation to prevent SQL injection.
    """
    query = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search users...',
            'maxlength': '100'
        }),
        validators=[
            MinLengthValidator(2, message="Search query must be at least 2 characters."),
            MaxLengthValidator(100, message="Search query must not exceed 100 characters.")
        ]
    )
    
    def clean_query(self):
        """
        Sanitize search query to prevent SQL injection and XSS attacks.
        """
        query = self.cleaned_data['query']
        
        # Remove SQL injection patterns
        sql_patterns = [
            r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|EXEC)\b)',
            r'(\b(OR|AND)\b\s*\d+\s*=\s*\d+)',
            r'(\-\-|\#|\/\*)',
            r'(\b(WAITFOR|DELAY)\b)'
        ]
        
        for pattern in sql_patterns:
            query = re.sub(pattern, '', query, flags=re.IGNORECASE)
        
        # Remove potentially dangerous characters
        query = re.sub(r'[<>&\"\';]', '', query)
        
        # Trim and validate
        query = query.strip()
        if len(query) < 2:
            raise forms.ValidationError("Search query must be at least 2 characters long.")
        
        return query