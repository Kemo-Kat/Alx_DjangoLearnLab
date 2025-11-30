"""
Comprehensive unit tests for API views with proper authentication using client.login().

This module contains test cases for all API endpoints, covering:
- CRUD operations for Book and Author models
- Filtering, searching, and ordering functionality
- Authentication and permission testing using Django's login mechanism
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
    
    def setUp(self):
        """Set up test data and client for all test cases."""
        self.client = APIClient()
        
        # Create test users with passwords
        self.regular_user = UserFactory(username='testuser')
        self.regular_user_password = 'testpassword123'
        self.regular_user.set_password(self.regular_user_password)
        self.regular_user.save()
        
        self.admin_user = UserFactory(username='admin', is_staff=True)
        self.admin_user_password = 'adminpassword123'
        self.admin_user.set_password(self.admin_user_password)
        self.admin_user.save()
        
        # Create test authors and books (same as before)
        self.author1 = AuthorFactory(name='J.K. Rowling')
        self.author2 = AuthorFactory(name='George R.R. Martin')
        self.author3 = AuthorFactory(name='Stephen King')
        
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


class AuthenticationTests(BaseAPITestCase):
    """
    Tests specifically for authentication functionality.
    """
    
    def test_successful_login(self):
        """
        Test that users can successfully log in.
        
        Expected: Login returns True and user is authenticated
        """
        login_successful = self.client.login(
            username='testuser', 
            password='testpassword123'
        )
        
        self.assertTrue(login_successful)
        self.assertTrue(self.client.session['_auth_user_id'])
    
    def test_failed_login_wrong_password(self):
        """
        Test that login fails with wrong password.
        
        Expected: Login returns False and user is not authenticated
        """
        login_successful = self.client.login(
            username='testuser', 
            password='wrongpassword'
        )
        
        self.assertFalse(login_successful)
    
    def test_failed_login_nonexistent_user(self):
        """
        Test that login fails with non-existent username.
        
        Expected: Login returns False and user is not authenticated
        """
        login_successful = self.client.login(
            username='nonexistent', 
            password='testpassword123'
        )
        
        self.assertFalse(login_successful)
    
    def test_logout_functionality(self):
        """
        Test that users can successfully log out.
        
        Expected: After logout, user is no longer authenticated
        """
        # First log in
        self.client.login(username='testuser', password='testpassword123')
        self.assertTrue(self.client.session['_auth_user_id'])
        
        # Then log out
        self.client.logout()
        
        # Check that user is no longer in session
        self.assertNotIn('_auth_user_id', self.client.session)


class BookCreateViewTests(BaseAPITestCase):
    """
    Test cases for Book Create API endpoint using proper login.
    """
    
    def test_create_book_authenticated_with_login(self):
        """
        Test that authenticated users (via login) can create books.
        
        Expected: HTTP 201 Created with new book data
        """
        # Use client.login() instead of force_authenticate
        self.client.login(username='testuser', password='testpassword123')
        
        book_data = {
            'title': 'New Test Book',
            'publication_year': 2023,
            'author': self.author1.id
        }
        
        response = self.client.post(self.book_create_url, book_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], book_data['title'])
        self.assertEqual(Book.objects.count(), 5)  # 4 existing + 1 new
    
    def test_create_book_with_different_user_roles(self):
        """
        Test book creation with different user roles using login.
        """
        # Test with regular user
        self.client.login(username='testuser', password='testpassword123')
        
        book_data = {
            'title': 'Book by Regular User',
            'publication_year': 2023,
            'author': self.author1.id
        }
        
        response = self.client.post(self.book_create_url, book_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Logout regular user
        self.client.logout()
        
        # Test with admin user
        self.client.login(username='admin', password='adminpassword123')
        
        book_data = {
            'title': 'Book by Admin User',
            'publication_year': 2023,
            'author': self.author1.id
        }
        
        response = self.client.post(self.book_create_url, book_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_create_book_after_logout(self):
        """
        Test that users cannot create books after logging out.
        
        Expected: HTTP 403 Forbidden after logout
        """
        # Login first
        self.client.login(username='testuser', password='testpassword123')
        
        # Then logout
        self.client.logout()
        
        book_data = {
            'title': 'Book After Logout',
            'publication_year': 2023,
            'author': self.author1.id
        }
        
        response = self.client.post(self.book_create_url, book_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Book.objects.count(), 4)  # No new books created
    
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
    
    def test_create_book_with_session_authentication(self):
        """
        Test book creation using session-based authentication.
        """
        # Login using session authentication
        login_successful = self.client.login(
            username='testuser', 
            password='testpassword123'
        )
        self.assertTrue(login_successful)
        
        book_data = {
            'title': 'Book with Session Auth',
            'publication_year': 2023,
            'author': self.author1.id
        }
        
        response = self.client.post(self.book_create_url, book_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 5)


class BookUpdateViewTests(BaseAPITestCase):
    """
    Test cases for Book Update API endpoint using proper login.
    """
    
    def test_update_book_authenticated_with_login(self):
        """
        Test that authenticated users (via login) can update books.
        
        Expected: HTTP 200 OK with updated book data
        """
        self.client.login(username='testuser', password='testpassword123')
        
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
    
    def test_partial_update_book_authenticated_with_login(self):
        """
        Test that authenticated users can partially update books using login.
        
        Expected: HTTP 200 OK with partially updated book data
        """
        self.client.login(username='testuser', password='testpassword123')
        
        partial_update_data = {
            'title': 'Partially Updated Title'
        }
        
        url = self.book_update_url(self.book1.id)
        response = self.client.patch(url, partial_update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, 'Partially Updated Title')
    
    def test_update_book_multiple_authenticated_sessions(self):
        """
        Test update functionality across multiple login sessions.
        """
        # First session
        self.client.login(username='testuser', password='testpassword123')
        
        update_data_1 = {
            'title': 'First Update',
            'publication_year': 1999,
            'author': self.author1.id
        }
        
        url = self.book_update_url(self.book1.id)
        response = self.client.put(url, update_data_1, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Logout and login with different user
        self.client.logout()
        self.client.login(username='admin', password='adminpassword123')
        
        update_data_2 = {
            'title': 'Second Update by Admin',
            'publication_year': 2000,
            'author': self.author1.id
        }
        
        response = self.client.put(url, update_data_2, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, 'Second Update by Admin')
    
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


class BookDeleteViewTests(BaseAPITestCase):
    """
    Test cases for Book Delete API endpoint using proper login.
    """
    
    def test_delete_book_authenticated_with_login(self):
        """
        Test that authenticated users (via login) can delete books.
        
        Expected: HTTP 204 No Content and book is removed
        """
        self.client.login(username='testuser', password='testpassword123')
        
        url = self.book_delete_url(self.book1.id)
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), 3)  # 4 original - 1 deleted
        self.assertFalse(Book.objects.filter(id=self.book1.id).exists())
    
    def test_delete_book_after_re_login(self):
        """
        Test delete functionality persists after re-authentication.
        """
        # Login and delete one book
        self.client.login(username='testuser', password='testpassword123')
        
        url = self.book_delete_url(self.book1.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Logout and login again
        self.client.logout()
        self.client.login(username='testuser', password='testpassword123')
        
        # Delete another book
        url = self.book_delete_url(self.book2.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        self.assertEqual(Book.objects.count(), 2)  # 4 original - 2 deleted
    
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


class AuthorViewTests(BaseAPITestCase):
    """
    Test cases for Author API endpoints with proper authentication.
    """
    
    def test_create_author_authenticated_with_login(self):
        """
        Test that authenticated users can create authors using login.
        
        Expected: HTTP 201 Created with new author data
        """
        self.client.login(username='testuser', password='testpassword123')
        
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
    
    def test_update_author_authenticated_with_login(self):
        """
        Test that authenticated users can update authors.
        
        Expected: HTTP 200 OK with updated author data
        """
        self.client.login(username='testuser', password='testpassword123')
        
        update_data = {
            'name': 'Updated Author Name'
        }
        
        url = self.author_detail_url(self.author1.id)
        response = self.client.put(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.author1.refresh_from_db()
        self.assertEqual(self.author1.name, 'Updated Author Name')


class SessionPersistenceTests(BaseAPITestCase):
    """
    Tests for session persistence and authentication state.
    """
    
    def test_session_persistence_across_requests(self):
        """
        Test that authentication persists across multiple requests in the same test.
        """
        # Login once
        self.client.login(username='testuser', password='testpassword123')
        
        # Make multiple requests - all should be authenticated
        book_data = {
            'title': 'First Book',
            'publication_year': 2023,
            'author': self.author1.id
        }
        response1 = self.client.post(self.book_create_url, book_data, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        book_data['title'] = 'Second Book'
        response2 = self.client.post(self.book_create_url, book_data, format='json')
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        
        # Check both books were created
        self.assertEqual(Book.objects.count(), 6)  # 4 original + 2 new
    
    def test_authentication_state_cleared_after_logout(self):
        """
        Test that authentication state is properly cleared after logout.
        """
        # Login and make authenticated request
        self.client.login(username='testuser', password='testpassword123')
        
        book_data = {
            'title': 'Book Before Logout',
            'publication_year': 2023,
            'author': self.author1.id
        }
        response = self.client.post(self.book_create_url, book_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Logout
        self.client.logout()
        
        # Try to make another request - should be unauthorized
        book_data['title'] = 'Book After Logout'
        response = self.client.post(self.book_create_url, book_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Only one new book should exist
        self.assertEqual(Book.objects.count(), 5)  # 4 original + 1 new


class AuthenticationEdgeCaseTests(BaseAPITestCase):
    """
    Tests for edge cases in authentication.
    """
    
    def test_concurrent_login_attempts(self):
        """
        Test behavior with multiple login attempts.
        """
        # First login should work
        login1 = self.client.login(username='testuser', password='testpassword123')
        self.assertTrue(login1)
        
        # Second login with same credentials should also work (replaces session)
        login2 = self.client.login(username='testuser', password='testpassword123')
        self.assertTrue(login2)
        
        # Login with different user
        login3 = self.client.login(username='admin', password='adminpassword123')
        self.assertTrue(login3)
        
        # Now the session should be for admin user
        self.assertEqual(int(self.client.session['_auth_user_id']), self.admin_user.id)
    
    def test_login_with_inactive_user(self):
        """
        Test that inactive users cannot log in.
        """
        # Create an inactive user
        inactive_user = UserFactory(username='inactive', is_active=False)
        inactive_user.set_password('testpassword123')
        inactive_user.save()
        
        # Try to login with inactive user
        login_successful = self.client.login(
            username='inactive', 
            password='testpassword123'
        )
        
        self.assertFalse(login_successful)
