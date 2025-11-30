from django.test import TestCase

# Create your tests here.
"""
Comprehensive unit tests for API views.

This module contains test cases for all API endpoints, covering:
- CRUD operations for Book and Author models
- Filtering, searching, and ordering functionality
- Authentication and permission testing
- Response data integrity and status codes
"""

import json
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from ..models import Author, Book
from .factories import UserFactory, AuthorFactory, BookFactory


class BaseAPITestCase(APITestCase):
    """
    Base test case with common setup and utility methods.
    """
   self.client.login 
    def setUp(self):
        """Set up test data and client for all test cases."""
        self.client = APIClient()
        
        # Create test users
        self.regular_user = UserFactory(username='testuser')
        self.admin_user = UserFactory(username='admin', is_staff=True)
        
        # Create test authors
        self.author1 = AuthorFactory(name='J.K. Rowling')
        self.author2 = AuthorFactory(name='George R.R. Martin')
        self.author3 = AuthorFactory(name='Stephen King')
        
        # Create test books
        self.book1 = BookFactory(
            title='Harry Potter and the Philosopher\'s Stone',
            publication_year=1997,
            author=self.author1
        )
        self.book2 = BookFactory(
            title='Harry Potter and the Chamber of Secrets',
            publication_year=1998,
            author=self.author1
        )
        self.book3 = BookFactory(
            title='A Game of Thrones',
            publication_year=1996,
            author=self.author2
        )
        self.book4 = BookFactory(
            title='The Shining',
            publication_year=1977,
            author=self.author3
        )
        
        # URLs
        self.book_list_url = reverse('book-list')
        self.book_detail_url = lambda pk: reverse('book-detail', kwargs={'pk': pk})
        self.book_create_url = reverse('book-create')
        self.book_update_url = lambda pk: reverse('book-update', kwargs={'pk': pk})
        self.book_delete_url = lambda pk: reverse('book-delete', kwargs={'pk': pk})
        self.author_list_url = reverse('author-list')
        self.author_detail_url = lambda pk: reverse('author-detail', kwargs={'pk': pk})


class BookListViewTests(BaseAPITestCase):
    """
    Test cases for Book List API endpoint.
    
    Tests filtering, searching, ordering, and basic list functionality.
    """
    
    def test_get_all_books_unauthenticated(self):
        """
        Test that unauthenticated users can retrieve all books.
        
        Expected: HTTP 200 OK with all books in response
        """
        response = self.client.get(self.book_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)
    
    def test_filter_books_by_publication_year(self):
        """
        Test filtering books by exact publication year.
        
        Expected: Only books from specified year are returned
        """
        url = f"{self.book_list_url}?publication_year=1997"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Harry Potter and the Philosopher\'s Stone')
    
    def test_filter_books_by_publication_year_range(self):
        """
        Test filtering books by publication year range.
        
        Expected: Only books within specified year range are returned
        """
        url = f"{self.book_list_url}?publication_year_min=1990&publication_year_max=2000"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # 3 books between 1990-2000
    
    def test_filter_books_by_author_name(self):
        """
        Test filtering books by author name (case-insensitive).
        
        Expected: Only books by specified author are returned
        """
        url = f"{self.book_list_url}?author_name=rowling"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # 2 books by Rowling
    
    def test_search_books_by_title(self):
        """
        Test searching books by title text.
        
        Expected: Only books matching search term are returned
        """
        url = f"{self.book_list_url}?search=harry"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # 2 Harry Potter books
    
    def test_search_books_by_author_name(self):
        """
        Test searching books by author name.
        
        Expected: Only books by authors matching search term are returned
        """
        url = f"{self.book_list_url}?search=king"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # 1 book by Stephen King
    
    def test_order_books_by_title_ascending(self):
        """
        Test ordering books by title in ascending order.
        
        Expected: Books are returned in alphabetical order by title
        """
        url = f"{self.book_list_url}?ordering=title"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [book['title'] for book in response.data]
        self.assertEqual(titles, sorted(titles))
    
    def test_order_books_by_publication_year_descending(self):
        """
        Test ordering books by publication year in descending order.
        
        Expected: Books are returned from newest to oldest
        """
        url = f"{self.book_list_url}?ordering=-publication_year"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        publication_years = [book['publication_year'] for book in response.data]
        self.assertEqual(publication_years, sorted(publication_years, reverse=True))
    
    def test_combined_filter_search_order(self):
        """
        Test combined filtering, searching, and ordering.
        
        Expected: Complex queries work correctly with multiple parameters
        """
        url = f"{self.book_list_url}?publication_year_min=1990&search=harry&ordering=-publication_year"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # 2 Harry Potter books after 1990
        self.assertGreater(response.data[0]['publication_year'], response.data[1]['publication_year'])


class BookDetailViewTests(BaseAPITestCase):
    """
    Test cases for Book Detail API endpoint.
    
    Tests retrieving individual book instances.
    """
    
    def test_get_book_detail_unauthenticated(self):
        """
        Test that unauthenticated users can retrieve book details.
        
        Expected: HTTP 200 OK with correct book data
        """
        url = self.book_detail_url(self.book1.id)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.book1.title)
        self.assertEqual(response.data['publication_year'], self.book1.publication_year)
        self.assertEqual(response.data['author'], self.author1.id)
    
    def test_get_nonexistent_book_detail(self):
        """
        Test retrieving details for a book that doesn't exist.
        
        Expected: HTTP 404 Not Found
        """
        url = self.book_detail_url(9999)  # Non-existent ID
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class BookCreateViewTests(BaseAPITestCase):
    """
    Test cases for Book Create API endpoint.
    
    Tests book creation with authentication and validation.
    """
    
    def test_create_book_authenticated(self):
        """
        Test that authenticated users can create books.
        
        Expected: HTTP 201 Created with new book data
        """
        self.client.force_authenticate(user=self.regular_user)
        
        book_data = {
            'title': 'New Test Book',
            'publication_year': 2023,
            'author': self.author1.id
        }
        
        response = self.client.post(self.book_create_url, book_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], book_data['title'])
        self.assertEqual(Book.objects.count(), 5)  # 4 existing + 1 new
    
    def test_create_book_unauthenticated(self):
        """
        Test that unauthenticated users cannot create books.
        
        Expected: HTTP 403 Forbidden
        """
        book_data = {
            'title': 'New Test Book',
            'publication_year': 2023,
            'author': self.author1.id
        }
        
        response = self.client.post(self.book_create_url, book_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Book.objects.count(), 4)  # No new books created
    
    def test_create_book_with_future_publication_year(self):
        """
        Test creating a book with future publication year (invalid).
        
        Expected: HTTP 400 Bad Request with validation error
        """
        self.client.force_authenticate(user=self.regular_user)
        
        book_data = {
            'title': 'Future Book',
            'publication_year': 2030,  # Future year
            'author': self.author1.id
        }
        
        response = self.client.post(self.book_create_url, book_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('publication_year', response.data)
    
    def test_create_book_with_invalid_author(self):
        """
        Test creating a book with non-existent author.
        
        Expected: HTTP 400 Bad Request with validation error
        """
        self.client.force_authenticate(user=self.regular_user)
        
        book_data = {
            'title': 'Book with Invalid Author',
            'publication_year': 2023,
            'author': 9999  # Non-existent author ID
        }
        
        response = self.client.post(self.book_create_url, book_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class BookUpdateViewTests(BaseAPITestCase):
    """
    Test cases for Book Update API endpoint.
    
    Tests book updates with authentication and validation.
    """
    
    def test_update_book_authenticated(self):
        """
        Test that authenticated users can update books.
        
        Expected: HTTP 200 OK with updated book data
        """
        self.client.force_authenticate(user=self.regular_user)
        
        update_data = {
            'title': 'Updated Book Title',
            'publication_year': 1999,
            'author': self.author1.id
        }
        
        url = self.book_update_url(self.book1.id)
        response = self.client.put(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, 'Updated Book Title')
    
    def test_partial_update_book_authenticated(self):
        """
        Test that authenticated users can partially update books.
        
        Expected: HTTP 200 OK with partially updated book data
        """
        self.client.force_authenticate(user=self.regular_user)
        
        partial_update_data = {
            'title': 'Partially Updated Title'
        }
        
        url = self.book_update_url(self.book1.id)
        response = self.client.patch(url, partial_update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, 'Partially Updated Title')
    
    def test_update_book_unauthenticated(self):
        """
        Test that unauthenticated users cannot update books.
        
        Expected: HTTP 403 Forbidden
        """
        update_data = {
            'title': 'Updated Book Title',
            'publication_year': 1999,
            'author': self.author1.id
        }
        
        url = self.book_update_url(self.book1.id)
        response = self.client.put(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_nonexistent_book(self):
        """
        Test updating a book that doesn't exist.
        
        Expected: HTTP 404 Not Found
        """
        self.client.force_authenticate(user=self.regular_user)
        
        update_data = {
            'title': 'Updated Book Title',
            'publication_year': 1999,
            'author': self.author1.id
        }
        
        url = self.book_update_url(9999)  # Non-existent ID
        response = self.client.put(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class BookDeleteViewTests(BaseAPITestCase):
    """
    Test cases for Book Delete API endpoint.
    
    Tests book deletion with authentication checks.
    """
    
    def test_delete_book_authenticated(self):
        """
        Test that authenticated users can delete books.
        
        Expected: HTTP 204 No Content and book is removed
        """
        self.client.force_authenticate(user=self.regular_user)
        
        url = self.book_delete_url(self.book1.id)
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), 3)  # 4 original - 1 deleted
        self.assertFalse(Book.objects.filter(id=self.book1.id).exists())
    
    def test_delete_book_unauthenticated(self):
        """
        Test that unauthenticated users cannot delete books.
        
        Expected: HTTP 403 Forbidden
        """
        url = self.book_delete_url(self.book1.id)
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Book.objects.count(), 4)  # No books deleted
        self.assertTrue(Book.objects.filter(id=self.book1.id).exists())
    
    def test_delete_nonexistent_book(self):
        """
        Test deleting a book that doesn't exist.
        
        Expected: HTTP 404 Not Found
        """
        self.client.force_authenticate(user=self.regular_user)
        
        url = self.book_delete_url(9999)  # Non-existent ID
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AuthorViewTests(BaseAPITestCase):
    """
    Test cases for Author API endpoints.
    
    Tests author list, detail, and creation functionality.
    """
    
    def test_get_all_authors_unauthenticated(self):
        """
        Test that unauthenticated users can retrieve all authors.
        
        Expected: HTTP 200 OK with all authors and nested books
        """
        response = self.client.get(self.author_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # 3 authors
    
    def test_get_author_detail_unauthenticated(self):
        """
        Test that unauthenticated users can retrieve author details.
        
        Expected: HTTP 200 OK with author data and nested books
        """
        url = self.author_detail_url(self.author1.id)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.author1.name)
        self.assertEqual(len(response.data['books']), 2)  # 2 books by this author
    
    def test_create_author_authenticated(self):
        """
        Test that authenticated users can create authors.
        
        Expected: HTTP 201 Created with new author data
        """
        self.client.force_authenticate(user=self.regular_user)
        
        author_data = {
            'name': 'New Test Author'
        }
        
        response = self.client.post(self.author_list_url, author_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], author_data['name'])
        self.assertEqual(Author.objects.count(), 4)  # 3 existing + 1 new
    
    def test_create_author_unauthenticated(self):
        """
        Test that unauthenticated users cannot create authors.
        
        Expected: HTTP 403 Forbidden
        """
        author_data = {
            'name': 'New Test Author'
        }
        
        response = self.client.post(self.author_list_url, author_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Author.objects.count(), 3)  # No new authors created


class ResponseDataIntegrityTests(BaseAPITestCase):
    """
    Test cases for response data integrity.
    
    Ensures that API responses contain correct and consistent data structures.
    """
    
    def test_book_response_data_structure(self):
        """
        Test that book responses contain all expected fields.
        
        Expected: Response contains all defined serializer fields
        """
        response = self.client.get(self.book_detail_url(self.book1.id))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_fields = ['id', 'title', 'publication_year', 'author', 'created_at', 'updated_at']
        for field in expected_fields:
            self.assertIn(field, response.data)
    
    def test_author_response_data_structure(self):
        """
        Test that author responses contain all expected fields with nested books.
        
        Expected: Response contains author fields and nested book data
        """
        response = self.client.get(self.author_detail_url(self.author1.id))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_fields = ['id', 'name', 'books', 'created_at', 'updated_at']
        for field in expected_fields:
            self.assertIn(field, response.data)
        
        # Check nested book structure
        self.assertIsInstance(response.data['books'], list)
        if len(response.data['books']) > 0:
            book_fields = ['id', 'title', 'publication_year', 'author', 'created_at', 'updated_at']
            for field in book_fields:
                self.assertIn(field, response.data['books'][0])
    
    def test_query_metadata_in_list_responses(self):
        """
        Test that list responses include query metadata.
        
        Expected: Response includes query_metadata with filter information
        """
        url = f"{self.book_list_url}?publication_year=1997&search=harry"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('query_metadata', response.data)
        self.assertIn('applied_filters', response.data['query_metadata'])
        self.assertIn('available_filters', response.data['query_metadata'])
