"""
Authentication System Test Script
"""
import os
import django
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from blog.models import UserProfile

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_blog.settings')
django.setup()

class AuthenticationTests(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = UserProfile.objects.get(user=self.user)
        self.profile.bio = 'Test bio'
        self.profile.save()
    
    def test_registration(self):
        """Test user registration"""
        url = reverse('register')
        
        # Test GET request
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/register.html')
        
        # Test POST with valid data
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Verify user was created
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_login(self):
        """Test user login"""
        url = reverse('login')
        
        # Test GET request
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Test POST with valid credentials
        data = {
            'username': 'testuser',
            'password': 'testpass123',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Test POST with invalid credentials
        data = {
            'username': 'testuser',
            'password': 'wrongpass',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)  # Stay on page
        self.assertContains(response, 'Invalid username or password')
    
    def test_logout(self):
        """Test user logout"""
        # Login first
        self.client.login(username='testuser', password='testpass123')
        
        # Test logout
        url = reverse('logout')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # Redirect after logout
    
    def test_profile_view(self):
        """Test profile view requires authentication"""
        url = reverse('profile')
        
        # Test without authentication (should redirect to login)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        
        # Test with authentication
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/profile.html')
    
    def test_profile_update(self):
        """Test profile update functionality"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('profile_edit')
        
        # Test GET request
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Test POST with valid data
        data = {
            'username': 'testuser',
            'email': 'updated@example.com',
            'first_name': 'Updated',
            'last_name': 'User',
            'bio': 'Updated bio',
            'location': 'New York',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Verify updates
        self.user.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(self.user.email, 'updated@example.com')
        self.assertEqual(self.profile.bio, 'Updated bio')
    
    def test_password_change(self):
        """Test password change functionality"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('change_password')
        
        # Test GET request
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Test POST with valid data
        data = {
            'old_password': 'testpass123',
            'new_password1': 'NewStrongPass456!',
            'new_password2': 'NewStrongPass456!',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Verify password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewStrongPass456!'))

if __name__ == '__main__':
    import unittest
    unittest.main()