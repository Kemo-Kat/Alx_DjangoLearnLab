from django import forms
from django.core.validators import MinLengthValidator, MaxLengthValidator, RegexValidator
from django.core.exceptions import ValidationError
from django.utils.html import escape
from django.utils.safestring import mark_safe
import re
from .models import Book  # Assuming you have a Book model

class ExampleForm(forms.Form):
    """
    Secure example form demonstrating Django security best practices.
    This form includes comprehensive input validation, sanitization,
    and protection against common web vulnerabilities.
    """
    
    # Basic field with validation
    title = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter book title',
            'maxlength': '100'
        }),
        validators=[
            MinLengthValidator(2, "Title must be at least 2 characters long."),
            MaxLengthValidator(100, "Title must not exceed 100 characters."),
            RegexValidator(
                regex=r'^[a-zA-Z0-9\s\-\.,!?\'"]+$',
                message="Title contains invalid characters.",
                code='invalid_title'
            )
        ],
        help_text="Enter the book title (2-100 characters)"
    )
    
    # Email field with custom validation
    author_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'author@example.com'
        }),
        help_text="Optional author email address"
    )
    
    # Text area with content sanitization
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Enter book description...',
            'maxlength': '500'
        }),
        validators=[MaxLengthValidator(500)],
        help_text="Book description (max 500 characters)"
    )
    
    # Choice field with safe options
    GENRE_CHOICES = [
        ('', 'Select a genre'),
        ('fiction', 'Fiction'),
        ('non-fiction', 'Non-Fiction'),
        ('science', 'Science'),
        ('technology', 'Technology'),
        ('biography', 'Biography'),
    ]
    
    genre = forms.ChoiceField(
        choices=GENRE_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    # Number field with range validation
    publication_year = forms.IntegerField(
        required=False,
        min_value=1000,
        max_value=2030,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'YYYY',
            'min': '1000',
            'max': '2030'
        }),
        help_text="Publication year (1000-2030)"
    )
    
    # URL field with validation
    book_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://example.com/book'
        }),
        help_text="Optional link to book information"
    )
    
    # Boolean field for terms acceptance
    terms_accepted = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label=mark_safe('I accept the <a href="/terms/" target="_blank">terms and conditions</a>')
    )

    def clean_title(self):
        """
        Custom validation and sanitization for title field.
        Prevents XSS and SQL injection attacks.
        """
        title = self.cleaned_data['title']
        
        # Remove leading/trailing whitespace
        title = title.strip()
        
        # Remove potentially dangerous characters for SQL injection
        sql_dangerous_chars = ["'", '"', ';', '--', '/*', '*/']
        for char in sql_dangerous_chars:
            title = title.replace(char, '')
        
        # Remove HTML tags to prevent XSS
        title = re.sub(r'<[^>]*>', '', title)
        
        # Escape any remaining special characters
        title = escape(title)
        
        # Check for minimum length after sanitization
        if len(title) < 2:
            raise ValidationError("Title must be at least 2 characters long after sanitization.")
        
        return title

    def clean_description(self):
        """
        Sanitize description field to allow safe formatting while preventing XSS.
        """
        description = self.cleaned_data['description']
        
        if not description:
            return description
        
        # Remove script tags and event handlers
        description = re.sub(r'<script.*?</script>', '', description, flags=re.IGNORECASE | re.DOTALL)
        description = re.sub(r'on\w+=\s*[\'\"].*?[\'\"]', '', description, flags=re.IGNORECASE)
        
        # Allow only safe HTML tags
        allowed_tags = ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'b', 'i']
        for tag in allowed_tags:
            description = re.sub(f'<{tag}[^>]*>', f'<{tag}>', description)
            description = re.sub(f'</{tag}>', f'</{tag}>', description)
        
        # Remove any other HTML tags
        description = re.sub(r'<(?!\/?(%s)\b)[^>]*>' % '|'.join(allowed_tags), '', description)
        
        # Escape any remaining unsafe content
        description = escape(description)
        
        return description

    def clean_publication_year(self):
        """
        Validate publication year with business logic.
        """
        year = self.cleaned_data['publication_year']
        
        if year:
            current_year = 2024  # This should be dynamic in a real application
            if year > current_year:
                raise ValidationError("Publication year cannot be in the future.")
            
            if year < 1000:
                raise ValidationError("Publication year must be 1000 or later.")
        
        return year

    def clean_book_url(self):
        """
        Validate URL and ensure it's from allowed domains in production.
        """
        url = self.cleaned_data['book_url']
        
        if url:
            # Basic URL validation
            if not re.match(r'^https?://', url):
                raise ValidationError("URL must start with http:// or https://")
            
            # In production, you might want to restrict to specific domains
            allowed_domains = ['example.com', 'books.example.org', 'archive.org']
            domain_allowed = any(domain in url for domain in allowed_domains)
            
            # For demonstration, we'll just log this
            # In production, you might want to raise an error for unauthorized domains
            if not domain_allowed:
                # Log this for security monitoring
                print(f"Warning: URL from unauthorized domain: {url}")
        
        return url

    def clean(self):
        """
        Form-wide validation for cross-field validation and additional security checks.
        """
        cleaned_data = super().clean()
        
        # Cross-field validation example
        title = cleaned_data.get('title')
        genre = cleaned_data.get('genre')
        
        # Example: Certain genres might require specific title patterns
        if genre == 'science' and title:
            science_keywords = ['science', 'physics', 'chemistry', 'biology']
            if not any(keyword in title.lower() for keyword in science_keywords):
                self.add_error('title', "Science books should have relevant keywords in the title.")
        
        # Additional security check: Prevent suspicious patterns
        description = cleaned_data.get('description', '')
        if self._contains_suspicious_patterns(description):
            self.add_error('description', "Description contains suspicious content.")
        
        return cleaned_data

    def _contains_suspicious_patterns(self, text):
        """
        Check for potential security threats in text.
        """
        if not text:
            return False
        
        suspicious_patterns = [
            r'javascript:',  # JavaScript protocol
            r'vbscript:',    # VBScript protocol
            r'data:',        # Data protocol
            r'onload=',      # Event handlers
            r'onerror=',
            r'onclick=',
            r'<iframe',      # Iframe tags
            r'<object',
            r'<embed',
            r'base64',       # Base64 encoded content
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False


class SecureSearchForm(forms.Form):
    """
    Secure search form with comprehensive input validation
    to prevent SQL injection and other attacks.
    """
    
    search_query = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search books...',
            'maxlength': '100'
        }),
        validators=[
            MinLengthValidator(2, "Search query must be at least 2 characters."),
            MaxLengthValidator(100, "Search query must not exceed 100 characters."),
            RegexValidator(
                regex=r'^[a-zA-Z0-9\s\-_.,!?@#$%&*()+=\[\]{}|:;"\'<>]+$',
                message="Search query contains invalid characters.",
                code='invalid_search'
            )
        ]
    )
    
    search_type = forms.ChoiceField(
        choices=[
            ('title', 'Title'),
            ('author', 'Author'),
            ('isbn', 'ISBN'),
            ('all', 'All Fields')
        ],
        initial='all',
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        })
    )
    
    results_per_page = forms.IntegerField(
        min_value=5,
        max_value=50,
        initial=10,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '5',
            'max': '50'
        })
    )

    def clean_search_query(self):
        """
        Sanitize search query to prevent SQL injection and XSS attacks.
        """
        query = self.cleaned_data['search_query']
        
        # Remove SQL injection patterns
        sql_patterns = [
            r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|EXEC|ALTER|CREATE)\b)',
            r'(\b(OR|AND)\b\s*\d+\s*=\s*\d+)',
            r'(\-\-|\#|\/\*|\*\/)',
            r'(\b(WAITFOR|DELAY|SHUTDOWN)\b)',
            r'(\b(XP_|SP_)\w+)'  # SQL Server extended procedures
        ]
        
        for pattern in sql_patterns:
            query = re.sub(pattern, '', query, flags=re.IGNORECASE)
        
        # Remove potentially dangerous characters for XSS
        query = re.sub(r'[<>&]', '', query)
        
        # Trim and validate length after sanitization
        query = query.strip()
        if len(query) < 2:
            raise ValidationError("Search query must be at least 2 characters long after sanitization.")
        
        return query


class BookModelForm(forms.ModelForm):
    """
    Secure ModelForm for Book model with additional validation and security measures.
    """
    
    class Meta:
        # Assuming you have a Book model
        # from .models import Book
        model = Book
        fields = ['title', 'author', 'isbn', 'publication_date', 'description', 'genre']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '200'
            }),
            'author': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '100'
            }),
            'isbn': forms.TextInput(attrs={
                'class': 'form-control',
                'pattern': '[0-9\-]{10,17}',
                'title': 'Enter ISBN in format 123-4-567-89012-3'
            }),
            'publication_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'maxlength': '1000'
            }),
            'genre': forms.Select(attrs={
                'class': 'form-control'
            })
        }
    
    def clean_title(self):
        """Secure title validation"""
        title = self.cleaned_data['title']
        return self._sanitize_text_field(title, field_name='title', min_length=2, max_length=200)
    
    def clean_author(self):
        """Secure author validation"""
        author = self.cleaned_data['author']
        return self._sanitize_text_field(author, field_name='author', min_length=2, max_length=100)
    
    def clean_description(self):
        """Secure description validation with HTML sanitization"""
        description = self.cleaned_data.get('description', '')
        if not description:
            return description
        
        # Remove all HTML tags for security
        description = re.sub(r'<[^>]*>', '', description)
        
        # Escape any special characters
        description = escape(description)
        
        if len(description) > 1000:
            raise ValidationError("Description must not exceed 1000 characters.")
        
        return description
    
    def clean_isbn(self):
        """ISBN validation"""
        isbn = self.cleaned_data['isbn']
        
        # Remove any non-digit characters except hyphens
        clean_isbn = re.sub(r'[^\d\-]', '', isbn)
        
        # Validate ISBN format (basic check)
        digits_only = re.sub(r'[^\d]', '', clean_isbn)
        if len(digits_only) not in [10, 13]:
            raise ValidationError("ISBN must be 10 or 13 digits long.")
        
        return clean_isbn
    
    def _sanitize_text_field(self, text, field_name, min_length=2, max_length=100):
        """
        Generic text field sanitization method.
        """
        if not text:
            return text
        
        # Remove dangerous characters
        text = re.sub(r'[<>&\"\';]', '', text)
        
        # Trim whitespace
        text = text.strip()
        
        # Validate length
        if len(text) < min_length:
            raise ValidationError(f"{field_name.title()} must be at least {min_length} characters long.")
        
        if len(text) > max_length:
            raise ValidationError(f"{field_name.title()} must not exceed {max_length} characters.")
        
        return text
    
    def clean(self):
        """
        Cross-field validation for Book model.
        """
        cleaned_data = super().clean()
        
        # Example: Ensure publication date is not in the future
        publication_date = cleaned_data.get('publication_date')
        if publication_date:
            from datetime import date
            if publication_date > date.today():
                self.add_error('publication_date', "Publication date cannot be in the future.")
        
        return cleaned_data


class BulkUploadForm(forms.Form):
    """
    Secure form for bulk book uploads with file validation.
    """
    
    FILE_TYPE_CHOICES = [
        ('csv', 'CSV File'),
        ('json', 'JSON File'),
    ]
    
    file = forms.FileField(
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv,.json'
        }),
        help_text="Upload CSV or JSON file with book data"
    )
    
    file_type = forms.ChoiceField(
        choices=FILE_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        })
    )
    
    overwrite_existing = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text="Overwrite existing books with same ISBN"
    )

    def clean_file(self):
        """
        Validate uploaded file for security.
        """
        uploaded_file = self.cleaned_data['file']
        
        # Check file size (max 5MB)
        max_size = 5 * 1024 * 1024  # 5MB
        if uploaded_file.size > max_size:
            raise ValidationError("File size must not exceed 5MB.")
        
        # Check file extension
        valid_extensions = ['.csv', '.json']
        file_name = uploaded_file.name.lower()
        if not any(file_name.endswith(ext) for ext in valid_extensions):
            raise ValidationError("Only CSV and JSON files are allowed.")
        
        # Check MIME type (basic check)
        valid_mime_types = ['text/csv', 'application/json', 'text/plain']
        if uploaded_file.content_type not in valid_mime_types:
            raise ValidationError("Invalid file type.")
        
        return uploaded_file
