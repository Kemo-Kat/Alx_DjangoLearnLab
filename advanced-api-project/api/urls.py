from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookList, BookViewSet
from django.urls import path
from . import views

router = DefaultRouter()
router.register(r'books_all', BookViewSet, basename='book_all')

urlpatterns = [
    # Route for the BookList view (ListAPIView)
    path('books/', BookList.as_view(), name='book-list'),

    # Include the router URLs for BookViewSet (all CRUD operations)
    path('', include(router.urls)),
]
"""
URL configuration for API application.
"""



urlpatterns = [
    # We'll implement views in the next section
]

"""
URL configuration for API application.

This module defines all API endpoints and maps them to appropriate views.
Each endpoint follows RESTful conventions for CRUD operations.
"""



# API URL Configuration
# API URL Configuration
urlpatterns = [
    # Book endpoints - Basic CRUD operations
    path('books/', views.BookListView.as_view(), name='book-list'),
    path('books/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),
    path('books/create/', views.BookCreateView.as_view(), name='book-create'),
    path('books/<int:pk>/update/', views.BookUpdateView.as_view(), name='book-update'),
    path('books/<int:pk>/delete/', views.BookDeleteView.as_view(), name='book-delete'),
    
    # Book endpoints - Custom views (enhanced functionality)
    path('books/custom/create/', views.CustomBookCreateView.as_view(), name='book-custom-create'),
    path('books/<int:pk>/custom/update/', views.CustomBookUpdateView.as_view(), name='book-custom-update'),
    
    # Author endpoints
    path('authors/', views.AuthorListView.as_view(), name='author-list'),
    path('authors/<int:pk>/', views.AuthorDetailView.as_view(), name='author-detail'),
]
"""
URL Patterns Explanation:

Book Endpoints:
- GET    /api/books/              - List all books (BookListView)
- GET    /api/books/<id>/         - Retrieve specific book (BookDetailView)
- POST   /api/books/create/       - Create new book (BookCreateView)
- PUT    /api/books/<id>/update/  - Update specific book (BookUpdateView)
- DELETE /api/books/<id>/delete/  - Delete specific book (BookDeleteView)

Author Endpoints:
- GET    /api/authors/            - List all authors (AuthorListView)
- POST   /api/authors/            - Create new author (AuthorListView)
- GET    /api/authors/<id>/       - Retrieve specific author (AuthorDetailView)
- PUT    /api/authors/<id>/       - Update specific author (AuthorDetailView)
- DELETE /api/authors/<id>/       - Delete specific author (AuthorDetailView)

Note: The URL patterns use explicit action names (create, update, delete) for clarity,
but could also follow RESTful conventions without action names.
"""
