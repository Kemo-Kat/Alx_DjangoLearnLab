"""
Data models for the API application.

This module defines the Author and Book models, establishing a one-to-many
relationship where one Author can have multiple Books.
"""

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class Author(models.Model):
    """
    Author model representing a book author.
    
    Fields:
        name (CharField): The name of the author (max 100 characters)
        created_at (DateTimeField): Timestamp when the author was created
        updated_at (DateTimeField): Timestamp when the author was last updated
    """
    
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Book(models.Model):
    """
    Book model representing a published book.
    
    Fields:
        title (CharField): The title of the book (max 200 characters)
        publication_year (IntegerField): The year the book was published
        author (ForeignKey): Reference to the Author who wrote the book
        created_at (DateTimeField): Timestamp when the book was created
        updated_at (DateTimeField): Timestamp when the book was last updated
    
    Relationship:
        Each Book has one Author (ForeignKey), but one Author can have multiple Books.
        This establishes a one-to-many relationship from Author to Book.
    """
    
    title = models.CharField(max_length=200)
    publication_year = models.IntegerField()
    author = models.ForeignKey(
        Author, 
        on_delete=models.CASCADE, 
        related_name='books'  # Enables reverse relationship: author.books.all()
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['title']
        # Ensure unique constraint for book titles per author
        unique_together = ['title', 'author']
    
    def clean(self):
        """Validate that publication year is not in the future."""
        current_year = timezone.now().year
        if self.publication_year > current_year:
            raise ValidationError({
                'publication_year': f'Publication year cannot be in the future. Current year is {current_year}.'
            })
    
    def save(self, *args, **kwargs):
        """Override save to call full_clean for validation."""
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.title} by {self.author.name}"