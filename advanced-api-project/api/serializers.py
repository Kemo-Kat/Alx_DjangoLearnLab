"""
Custom serializers for the API application.

This module defines serializers for the Author and Book models, including
custom validation and handling of nested relationships.
"""

from rest_framework import serializers
from django.utils import timezone
from .models import Author, Book


class BookSerializer(serializers.ModelSerializer):
    """
    Serializer for the Book model.
    
    Handles serialization/deserialization of Book instances and includes
    custom validation for the publication_year field.
    
    Fields:
        id (IntegerField): The unique identifier for the book
        title (CharField): The title of the book
        publication_year (IntegerField): The year the book was published
        author (PrimaryKeyRelatedField): The ID of the author
        created_at (DateTimeField): When the book was created
        updated_at (DateTimeField): When the book was last updated
    
    Validation:
        Custom validation ensures publication_year is not in the future.
    """
    
    class Meta:
        model = Book
        fields = ['id', 'title', 'publication_year', 'author', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_publication_year(self, value):
        """
        Validate that publication_year is not in the future.
        
        Args:
            value (int): The publication year to validate
            
        Returns:
            int: The validated publication year
            
        Raises:
            serializers.ValidationError: If publication year is in the future
        """
        current_year = timezone.now().year
        if value > current_year:
            raise serializers.ValidationError(
                f'Publication year cannot be in the future. Current year is {current_year}.'
            )
        return value
    
    def validate(self, data):
        """
        Object-level validation for Book instances.
        
        Args:
            data (dict): The data to validate
            
        Returns:
            dict: The validated data
        """
        # Additional validation can be added here if needed
        return data


class AuthorSerializer(serializers.ModelSerializer):
    """
    Serializer for the Author model with nested book relationships.
    
    Handles serialization/deserialization of Author instances and includes
    a nested representation of related books using BookSerializer.
    
    Fields:
        id (IntegerField): The unique identifier for the author
        name (CharField): The name of the author
        books (BookSerializer): Nested serializer for related books (read-only)
        created_at (DateTimeField): When the author was created
        updated_at (DateTimeField): When the author was last updated
    
    Relationship Handling:
        The 'books' field uses BookSerializer to serialize all books
        related to this author. This creates a nested representation
        where each author includes a list of their books.
    """
    
    books = BookSerializer(many=True, read_only=True)
    
    class Meta:
        model = Author
        fields = ['id', 'name', 'books', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_name(self, value):
        """
        Validate the author's name.
        
        Args:
            value (str): The author name to validate
            
        Returns:
            str: The validated author name
        """
        if len(value.strip()) < 2:
            raise serializers.ValidationError('Author name must be at least 2 characters long.')
        return value.strip()


class AuthorCreateSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for creating authors without nested books.
    
    This serializer is used specifically for creating new author instances
    without the overhead of nested book data.
    """
    
    class Meta:
        model = Author
        fields = ['id', 'name']