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