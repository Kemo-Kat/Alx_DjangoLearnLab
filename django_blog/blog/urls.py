"""
URL configuration for django_blog project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views
from .views import (
    PostListView, PostDetailView, PostCreateView, 
    PostUpdateView, PostDeleteView, RegisterView,
    ProfileView, ProfileUpdateView, UserPostsView,
    UserCommentsView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),  # Blog app URLs
    path('accounts/', include('django.contrib.auth.urls')),  # Authentication URLs
    path('', views.PostListView.as_view(), name='home'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('post/new/', views.PostCreateView.as_view(), name='post_create'),
    path('post/<int:pk>/update/', views.PostUpdateView.as_view(), name='post_update'),
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    path('search/', views.search_posts, name='search'),

     # Core blog URLs
    path('', PostListView.as_view(), name='home'),
    path('posts/', PostListView.as_view(), name='post_list'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('post/<int:pk>/<slug:slug>/', PostDetailView.as_view(), name='post_detail_slug'),
    
    # CRUD Operations
    path('post/new/', PostCreateView.as_view(), name='post_create'),
    path('post/<int:pk>/edit/', PostUpdateView.as_view(), name='post_edit'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
    
    # User-specific views
    path('posts/drafts/', DraftListView.as_view(), name='post_drafts'),
    path('user/<str:username>/posts/', UserPostListView.as_view(), name='user_posts'),
    
    # Post interactions
    path('post/<int:pk>/like/', views.post_like_view, name='post_like'),
    path('post/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:pk>/delete/', views.delete_comment, name='delete_comment'),
    
    # Comment URLs
    path('post/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:pk>/edit/', views.edit_comment, name='edit_comment'),
    path('comment/<int:pk>/delete/', views.delete_comment, name='delete_comment'),

    # Search
    path('search/', views.search_posts, name='search'),
    
    # Authentication URLs
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', views.custom_login_view, name='login'),
    path('logout/', views.custom_logout_view, name='logout'),
    
    # Profile URLs
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', ProfileUpdateView.as_view(), name='profile_edit'),
    path('profile/change-password/', views.change_password_view, name='change_password'),
    path('profile/posts/', UserPostsView.as_view(), name='user_posts'),
    path('profile/comments/', UserCommentsView.as_view(), name='user_comments'),
    path('profile/delete-account/', views.delete_account_view, name='delete_account'),

    # Tag and Search URLs
    path('search/', views.search_posts, name='search'),
    path('tags/', views.tag_cloud, name='tag_cloud'),
    path('tags/<slug:tag_slug>/', views.posts_by_tag, name='posts_by_tag'),
    
 # Password reset URLs
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='blog/password_reset.html',
             email_template_name='blog/password_reset_email.html',
             subject_template_name='blog/password_reset_subject.txt'
         ), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='blog/password_reset_done.html'
         ), 
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='blog/password_reset_confirm.html'
         ), 
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='blog/password_reset_complete.html'
         ), 
         name='password_reset_complete'),

    # Comment URLs
    path('post/<int:pk>/comment/', views.add_comment, name='add_comment'),
    
    # Password reset URLs (using Django's built-in views)
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='blog/password_reset.html',
             email_template_name='blog/password_reset_email.html',
             subject_template_name='blog/password_reset_subject.txt'
         ), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='blog/password_reset_done.html'
         ), 
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='blog/password_reset_confirm.html'
         ), 
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='blog/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns = [
    path('admin/', admin.site.urls),
]
