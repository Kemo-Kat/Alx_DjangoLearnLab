"""
Custom filters for the API application.

This module defines advanced filtering capabilities for Book and Author models,
including range filters, choice filters, and custom lookup filters.
"""

import django_filters
from django_filters import rest_framework as filters
from .models import Book, Author


class BookFilter(filters.FilterSet):
    """
    Advanced filter set for Book model.
    
    Provides comprehensive filtering options including:
    - Exact match filtering
    - Range filtering for publication years
    - Case-insensitive contains filtering
    - Custom choice-based filtering
    
    Usage Examples:
    - /api/books/?publication_year=2020
    - /api/books/?publication_year_min=2010&publication_year_max=2020
    - /api/books/?title_icontains=harry
    - /api/books/?author_name=J.K.%20Rowling
    """
    
    # Exact match filters
    publication_year = filters.NumberFilter(field_name='publication_year', lookup_expr='exact')
    author = filters.NumberFilter(field_name='author__id', lookup_expr='exact')
    
    # Range filters for publication year
    publication_year_min = filters.NumberFilter(
        field_name='publication_year', 
        lookup_expr='gte',
        help_text='Filter books published in or after this year'
    )
    publication_year_max = filters.NumberFilter(
        field_name='publication_year', 
        lookup_expr='lte',
        help_text='Filter books published in or before this year'
    )
    
    # Case-insensitive contains filter for title
    title_icontains = filters.CharFilter(
        field_name='title', 
        lookup_expr='icontains',
        help_text='Filter books whose title contains this text (case-insensitive)'
    )
    
    # Filter by author name
    author_name = filters.CharFilter(
        field_name='author__name', 
        lookup_expr='icontains',
        help_text='Filter books by author name (case-insensitive)'
    )
    
    # Choice-based filter for publication decade
    publication_decade = filters.NumberFilter(
        method='filter_by_decade',
        help_text='Filter books by publication decade (e.g., 2020 for 2020-2029)'
    )
    
    class Meta:
        model = Book
        fields = {
            'title': ['exact', 'icontains'],
            'publication_year': ['exact', 'gte', 'lte'],
            'author__name': ['exact', 'icontains'],
        }
    
    def filter_by_decade(self, queryset, name, value):
        """
        Custom filter method to filter books by publication decade.
        
        Args:
            queryset: The original queryset
            name: The field name
            value: The decade value (e.g., 2020 for 2020-2029)
            
        Returns:
            Filtered queryset containing books from the specified decade
        """
        if value:
            year_min = value
            year_max = value + 9
            return queryset.filter(publication_year__gte=year_min, publication_year__lte=year_max)
        return queryset
    
    @property
    def qs(self):
        """
        Override the default queryset to add custom ordering if no ordering is specified.
        """
        queryset = super().qs
        # If no explicit ordering is provided, order by title
        if not self.data.get('ordering'):
            queryset = queryset.order_by('title')
        return queryset


class AuthorFilter(filters.FilterSet):
    """
    Filter set for Author model with book count filtering.
    
    Provides filtering options for authors including book count ranges.
    """
    
    # Filter by number of books
    min_books = filters.NumberFilter(method='filter_min_books')
    max_books = filters.NumberFilter(method='filter_max_books')
    
    name_icontains = filters.CharFilter(
        field_name='name', 
        lookup_expr='icontains',
        help_text='Filter authors whose name contains this text (case-insensitive)'
    )
    
    class Meta:
        model = Author
        fields = ['name']
    
    def filter_min_books(self, queryset, name, value):
        """
        Filter authors with at least the specified number of books.
        """
        if value:
            return queryset.annotate(book_count=models.Count('books')).filter(book_count__gte=value)
        return queryset
    
    def filter_max_books(self, queryset, name, value):
        """
        Filter authors with at most the specified number of books.
        """
        if value:
            return queryset.annotate(book_count=models.Count('books')).filter(book_count__lte=value)
        return queryset