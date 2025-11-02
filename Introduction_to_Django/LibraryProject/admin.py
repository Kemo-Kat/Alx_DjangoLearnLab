# LibraryProject/bookshelf/admin.py
from django.contrib import admin

# Import the Book model from your models.py file
from .models import Book

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    # Display fields in the list view
    list_display = ['title', 'author', 'publication_year', 'is_available']
    
    # Add filters for easy navigation
    list_filter = ['publication_year', 'author', 'is_available']
    
    # Enable search functionality
    search_fields = ['title', 'author', 'description']
    
    # Fields to display in the detail view
    fieldsets = [
        ('Basic Information', {
            'fields': ['title', 'author', 'publication_year']
        }),
        ('Additional Details', {
            'fields': ['description', 'isbn', 'is_available'],
            'classes': ['collapse']
        })
    ]
