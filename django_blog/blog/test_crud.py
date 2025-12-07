
"""
CRUD Operations Test Script
"""
import os
import django
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from blog.models import Post, Comment
from django.core.files.uploadedfile import SimpleUploadedFile

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_blog.settings')
django.setup()

class CRUDTests(TestCase):
    def setUp(self):
        """Set up test users and data"""
        self.client = Client()
        
        # Create users
        self.author = User.objects.create_user(
            username='author',
            email='author@example.com',
            password='authorpass123'
        )
        
        self.other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='otherpass123'
        )
        
        # Create test post
        self.post = Post.objects.create(
            title='Test Post',
            content='This is a test post content.',
            author=self.author,
            status='published'
        )
        
        # Create draft post
        self.draft_post = Post.objects.create(
            title='Draft Post',
            content='This is a draft post.',
            author=self.author,
            status='draft'
        )
    
    def test_post_list_view(self):
        """Test viewing all posts"""
        url = reverse('post_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_list.html')
        self.assertContains(response, 'Test Post')
        self.assertNotContains(response, 'Draft Post')  # Drafts shouldn't appear
    
    def test_post_detail_view(self):
        """Test viewing individual post"""
        url = reverse('post_detail', args=[self.post.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_detail.html')
        self.assertContains(response, self.post.title)
        self.assertContains(response, self.post.content)
    
    def test_post_create_authenticated(self):
        """Test creating post when authenticated"""
        self.client.login(username='author', password='authorpass123')
        url = reverse('post_create')
        
        # Test GET request
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_form.html')
        
        # Test POST with valid data
        data = {
            'title': 'New Test Post',
            'content': 'This is the content of the new test post.',
            'excerpt': 'Brief excerpt of the post.',
            'status': 'published',
            'tags_input': 'django, testing, python'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Verify post was created
        self.assertTrue(Post.objects.filter(title='New Test Post').exists())
        new_post = Post.objects.get(title='New Test Post')
        self.assertEqual(new_post.author, self.author)
        self.assertEqual(new_post.status, 'published')
    
    def test_post_create_unauthenticated(self):
        """Test creating post when not authenticated"""
        url = reverse('post_create')
        response = self.client.get(url)
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
    
    def test_post_update_author(self):
        """Test updating post as author"""
        self.client.login(username='author', password='authorpass123')
        url = reverse('post_edit', args=[self.post.pk])
        
        # Test GET request
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Test POST with updated data
        data = {
            'title': 'Updated Test Post',
            'content': 'Updated content.',
            'status': 'published',
            'tags_input': 'updated, tags'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        
        # Verify post was updated
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Updated Test Post')
        self.assertEqual(self.post.content, 'Updated content')
    
    def test_post_update_non_author(self):
        """Test updating post as non-author"""
        self.client.login(username='other', password='otherpass123')
        url = reverse('post_edit', args=[self.post.pk])
        
        # Should redirect to post detail
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('post_detail', args=[self.post.pk]))
    
    def test_post_delete_author(self):
        """Test deleting post as author"""
        self.client.login(username='author', password='authorpass123')
        url = reverse('post_delete', args=[self.post.pk])
        
        # Test GET request (confirmation page)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Test POST (actual deletion)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Verify post was deleted
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())
    
    def test_post_delete_non_author(self):
        """Test deleting post as non-author"""
        self.client.login(username='other', password='otherpass123')
        url = reverse('post_delete', args=[self.post.pk])
        
        # Should redirect to post detail
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('post_detail', args=[self.post.pk]))
    
    def test_draft_list_view(self):
        """Test viewing drafts"""
        self.client.login(username='author', password='authorpass123')
        url = reverse('post_drafts')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_drafts.html')
        self.assertContains(response, 'Draft Post')
        self.assertNotContains(response, 'Test Post')  # Published posts shouldn't appear
    
    def test_comment_functionality(self):
        """Test commenting on posts"""
        self.client.login(username='other', password='otherpass123')
        url = reverse('add_comment', args=[self.post.pk])
        
        # Test adding comment
        data = {'content': 'This is a test comment.'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        
        # Verify comment was created
        self.assertTrue(self.post.comments.filter(content='This is a test comment.').exists())
    
    def test_like_functionality(self):
        """Test liking posts"""
        self.client.login(username='other', password='otherpass123')
        url = reverse('post_like', args=[self.post.pk])
        
        # Test liking
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.post.likes.filter(username='other').exists())
        
        # Test unliking
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.post.likes.filter(username='other').exists())
    
    def test_search_functionality(self):
        """Test post search"""
        url = reverse('search')
        
        # Test search with query
        response = self.client.get(url, {'q': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')
        
        # Test search with no results
        response = self.client.get(url, {'q': 'nonexistent'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Test Post')

if __name__ == '__main__':
    import unittest
    unittest.main()