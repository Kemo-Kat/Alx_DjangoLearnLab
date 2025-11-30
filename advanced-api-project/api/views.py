from django.shortcuts import render

# Create your views here.
from rest_framework import generics, viewsets, permissions, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Book, Author
from .serializers import AuthorSerializer, BookSerializer, AuthorCreateSerializer
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .permissions import IsAuthenticatedOrReadOnly, IsAdminOrReadOnly
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .filters import BookFilter, AuthorFilter
from django_filters import rest_framework


class BookListView(generics.ListAPIView):
    """
    Enhanced List view for retrieving books with advanced filtering, searching, and ordering.
    
    This view provides comprehensive query capabilities:
    - Filtering: Filter by publication year, author, title, and custom ranges
    - Searching: Text search across title and author names
    - Ordering: Sort by any field with ascending or descending order
    
    Filter Backends:
        DjangoFilterBackend: For field-based filtering using BookFilter
        SearchFilter: For text-based searching across multiple fields
        OrderingFilter: For sorting results by specified fields
    
    Example Usage:
        GET /api/books/?publication_year=2020
        GET /api/books/?search=harry&ordering=-publication_year
        GET /api/books/?publication_year_min=2010&publication_year_max=2020
        GET /api/books/?title_icontains=potter&author_name=Rowling
        GET /api/books/?ordering=title,-publication_year
    """
    filters.OrderingFilter
    filters.SearchFilter
    queryset = Book.objects.all().select_related('author')
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]
    
    # Filter configuration
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BookFilter  # Use our custom filter class
    
    # Search configuration - define which fields are searchable
    search_fields = [
        'title',           # Exact title matching
        'author__name',    # Author name matching
        '^title',          # Title starts with search term
    ]
    
    # Ordering configuration - define which fields can be used for ordering
    ordering_fields = [
        'title',
        'publication_year', 
        'created_at', 
        'updated_at',
        'author__name',    # Order by author name
    ]
    
    # Default ordering when no ordering specified
    ordering = ['title']
    
    def get_queryset(self):
        """
        Enhance the base queryset with additional optimizations.
        
        Returns:
            Optimized queryset with select_related and prefetch_related
        """
        queryset = super().get_queryset()
        return queryset.select_related('author')
    
    def list(self, request, *args, **kwargs):
        """
        Custom list method to provide enhanced response with query metadata.
        
        Overrides the default list method to include information about
        applied filters, search, and ordering in the response.
        """
        response = super().list(request, *args, **kwargs)
        
        # Add query metadata to the response
        query_params = request.query_params
        applied_filters = {}
        
        # Capture applied filters
        for param, value in query_params.items():
            if param in ['search', 'ordering']:
                applied_filters[param] = value
            elif param in BookFilter.get_filters():
                applied_filters[param] = value
        
        # Add metadata to response
        response.data['query_metadata'] = {
            'total_results': len(response.data['results']) if 'results' in response.data else len(response.data),
            'applied_filters': applied_filters,
            'available_filters': {
                'search_fields': self.search_fields,
                'ordering_fields': self.ordering_fields,
                'filter_fields': list(BookFilter.get_filters().keys()),
            }
        }
        
        return response


class BookDetailView(generics.RetrieveAPIView):
    """
    Detail view for retrieving a single book by ID.
    Maintains basic functionality without filtering capabilities.
    """
    queryset = Book.objects.all().select_related('author')
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'pk'


class AuthorListView(generics.ListCreateAPIView):
    """
    Enhanced Author list view with filtering and search capabilities.
    
    Provides:
    - Filtering by name and book count
    - Search across author names
    - Ordering by various fields
    
    Example Usage:
        GET /api/authors/?name_icontains=rowling
        GET /api/authors/?min_books=5
        GET /api/authors/?search=J.K.&ordering=name
    """
    
    queryset = Author.objects.all().prefetch_related('books')
    permission_classes = [permissions.AllowAny]
    
    # Filter configuration for authors
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = AuthorFilter
    search_fields = ['name', '^name']  # Search by name
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['name']  # Default ordering by name
    
    def get_serializer_class(self):
        """Use different serializers for different actions."""
        if self.request.method == 'POST':
            return AuthorCreateSerializer
        return AuthorSerializer
    
    def get_permissions(self):
        """Apply different permissions based on HTTP method."""
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]


# Keep all other existing views (BookCreateView, BookUpdateView, etc.)
# They remain unchanged as filtering primarily applies to list views

class BookCreateView(generics.CreateAPIView):
    """Create view for books (unchanged from previous implementation)."""
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class BookUpdateView(generics.UpdateAPIView):
    """Update view for books (unchanged from previous implementation)."""
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'pk'


class BookDeleteView(generics.DestroyAPIView):
    """Delete view for books (unchanged from previous implementation)."""
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'pk'

class BookList(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]  # Add authentication requirement


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]  # Only admins can modify
        else:
            # Authenticated users can view
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

"""
Custom views for the API application.

This module implements generic views for CRUD operations on Book and Author models,
including custom permissions, filtering, and view behavior customization.
"""




class BookListView(generics.ListAPIView):
    """
    List view for retrieving all books.
    
    Provides read-only access to a list of all Book instances.
    Supports filtering, searching, and ordering.
    
    Permissions:
        AllowAny - Read access for all users (authenticated or not)
    """
    queryset = Book.objects.all().select_related('author')
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]
    
    # Enable filtering, searching, and ordering
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['author', 'publication_year']
    search_fields = ['title', 'author__name']
    ordering_fields = ['title', 'publication_year', 'created_at']
    ordering = ['title']  # Default ordering


class BookDetailView(generics.RetrieveAPIView):
    """
    Detail view for retrieving a single book by ID.
    
    Provides read-only access to a specific Book instance.
    
    Permissions:
        AllowAny - Read access for all users (authenticated or not)
    """
    queryset = Book.objects.all().select_related('author')
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'pk'


class BookCreateView(generics.CreateAPIView):
    """
    Create view for adding a new book.
    
    Handles creation of new Book instances with data validation.
    Includes custom permission checks.
    
    Permissions:
        IsAuthenticated - Only authenticated users can create books
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        """
        Customize the creation process.
        
        Args:
            serializer: The BookSerializer instance with validated data
        """
        # Additional business logic can be added here
        # For example: logging, notifications, etc.
        serializer.save()
        
        # Custom response message could be added here
        # self.headers.update({'Custom-Header': 'Book created successfully'})


class BookUpdateView(generics.UpdateAPIView):
    """
    Update view for modifying an existing book.
    
    Handles partial and complete updates of Book instances.
    Includes custom validation and permission checks.
    
    Permissions:
        IsAuthenticated - Only authenticated users can update books
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'
    
    def perform_update(self, serializer):
        """
        Customize the update process.
        
        Args:
            serializer: The BookSerializer instance with validated data
        """
        # Additional business logic can be added here
        # For example: version tracking, audit logging, etc.
        serializer.save()


class BookDeleteView(generics.DestroyAPIView):
    """
    Delete view for removing a book.
    
    Handles deletion of Book instances with proper permission checks.
    
    Permissions:
        IsAuthenticated - Only authenticated users can delete books
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'
    
    def perform_destroy(self, instance):
        """
        Customize the deletion process.
        
        Args:
            instance: The Book instance to be deleted
        """
        # Additional business logic can be added here
        # For example: archiving, soft delete, etc.
        instance.delete()


class AuthorListView(generics.ListCreateAPIView):
    """
    Combined list and create view for Author model.
    
    Provides:
    - List: Read-only access to all authors (with nested books)
    - Create: Creation of new authors (simplified serializer)
    
    Permissions:
        List: AllowAny
        Create: IsAuthenticated
    """
    queryset = Author.objects.all().prefetch_related('books')
    permission_classes = [permissions.AllowAny]
    
    def get_serializer_class(self):
        """
        Use different serializers for different actions.
        
        Returns:
            Serializer class based on HTTP method
        """
        if self.request.method == 'POST':
            return AuthorCreateSerializer
        return AuthorSerializer
    
    def get_permissions(self):
        """
        Apply different permissions based on HTTP method.
        
        Returns:
            Permission classes list
        """
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]


class AuthorDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Combined retrieve, update, delete view for Author model.
    
    Provides detailed operations for a single Author instance.
    
    Permissions:
        Retrieve: AllowAny
        Update/Delete: IsAuthenticated
    """
    queryset = Author.objects.all().prefetch_related('books')
    lookup_field = 'pk'
    
    def get_serializer_class(self):
        """
        Use different serializers for different actions.
        
        Returns:
            Serializer class based on HTTP method
        """
        if self.request.method in ['PUT', 'PATCH']:
            return AuthorCreateSerializer
        return AuthorSerializer
    
    def get_permissions(self):
        """
        Apply different permissions based on HTTP method.
        
        Returns:
            Permission classes list
        """
        if self.request.method in ['GET']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

class CustomBookCreateView(generics.CreateAPIView):
    """
    Custom create view with enhanced validation and response handling.
    
    This view demonstrates customizing the default CreateAPIView behavior
    with additional validation, response formatting, and error handling.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """
        Custom create method with enhanced response handling.
        
        Overrides the default create method to:
        - Add custom headers
        - Modify response format
        - Implement additional validation
        """
        serializer = self.get_serializer(data=request.data)
        
        # Custom validation before default validation
        publication_year = request.data.get('publication_year')
        if publication_year and int(publication_year) < 1000:
            return Response(
                {"error": "Publication year seems invalid."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Proceed with default validation and creation
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Custom success response
        headers = self.get_success_headers(serializer.data)
        response_data = {
            "message": "Book created successfully",
            "data": serializer.data,
            "status": "success"
        }
        
        return Response(
            response_data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )


class CustomBookUpdateView(generics.UpdateAPIView):
    """
    Custom update view with enhanced validation and response handling.
    
    This view demonstrates customizing the default UpdateAPIView behavior
    with additional business logic and response formatting.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'
    
    def update(self, request, *args, **kwargs):
        """
        Custom update method with enhanced response handling.
        
        Overrides the default update method to:
        - Track changes
        - Provide detailed response messages
        - Implement partial update restrictions
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # Track original values for auditing
        original_title = instance.title
        original_year = instance.publication_year
        
        self.perform_update(serializer)
        
        # Custom success response with change information
        response_data = {
            "message": "Book updated successfully",
            "data": serializer.data,
            "changes": {
                "title_changed": original_title != instance.title,
                "year_changed": original_year != instance.publication_year
            },
            "status": "success"
        }
        
        return Response(response_data)


# Update BookCreateView to use custom permissions
class BookCreateView(generics.CreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Updated to custom permission
    
    # ... rest of the code remains the same
