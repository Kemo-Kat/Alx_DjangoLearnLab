
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q, Count, F
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db import transaction
from taggit.models import Tag
from django.core.exceptions import PermissionDenied
from .models import Post, Comment, UserProfile
from .forms import (
    CustomUserCreationForm, CustomAuthenticationForm, 
    UserProfileForm, PasswordChangeCustomForm, 
    PostForm, CommentForm, SearchForm)
# Create your views here.

class PostListView(ListView):
    """Display all published blog posts with filtering"""
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10
    ordering = ['-published_date']
    
    def get_queryset(self):
        queryset = Post.objects.filter(status='published').select_related('author')
        
        # Filter by tag
        tag_slug = self.request.GET.get('tag')
        if tag_slug:
            queryset = queryset.filter(tags__slug__in=[tag_slug])
        
        # Filter by author
        author_username = self.request.GET.get('author')
        if author_username:
            queryset = queryset.filter(author__username=author_username)
        
        # Search functionality
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(excerpt__icontains=search_query) |
                Q(tags__name__icontains=search_query)
            ).distinct()
        
        # Annotate with comment count
        queryset = queryset.annotate(comment_count=Count('comments'))
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get popular tags
        context['popular_tags'] = Tag.objects.annotate(
            num_posts=Count('taggit_taggeditem_items')
        ).order_by('-num_posts')[:10]
        
        # Get recent comments
        context['recent_comments'] = Comment.objects.filter(
            approved=True
        ).select_related('author', 'post').order_by('-created_date')[:5]
        
        # Get popular posts (most viewed)
        context['popular_posts'] = Post.objects.filter(
            status='published'
        ).order_by('-views')[:5]
        
        # Search form
        context['search_form'] = PostSearchForm(self.request.GET or None)
        
        # Add filter info
        tag_slug = self.request.GET.get('tag')
        if tag_slug:
            context['current_tag'] = get_object_or_404(Tag, slug=tag_slug)
        
        author_username = self.request.GET.get('author')
        if author_username:
            context['current_author'] = get_object_or_404(User, username=author_username)
        
        return context

class PostDetailView(DetailView):
    """Display individual blog post with comments"""
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    
    def get_queryset(self):
        return Post.objects.select_related('author').prefetch_related('tags')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['comments'] = post.comments.all().order_by('created_at')
        context['comment_form'] = CommentForm()
        
        post_tags_ids = post.tags.values_list('id', flat=True)
        related_posts = Post.objects.filter(
            status='published',
            tags__in=post_tags_ids
        ).exclude(pk=post.pk).distinct()[:3]
        
        context.update({
            'related_posts': related_posts,
            'search_form': SearchForm(),
        })

        # Increment view count
        post.increment_views()
        
        # Get approved comments with replies
        comments = post.comments.filter(
            approved=True, 
            parent__isnull=True
        ).select_related('author').prefetch_related('replies')
        
        # Get related posts (same tags)
        related_posts = Post.objects.filter(
            status='published',
            tags__in=post.tags.all()
        ).exclude(pk=post.pk).distinct()[:3]
        
        context.update({
            'comments': comments,
            'comment_form': CommentForm(),
            'related_posts': related_posts,
            'total_comments': post.comments.filter(approved=True).count(),
            'user_has_liked': post.likes.filter(id=self.request.user.id).exists() if self.request.user.is_authenticated else False,
        })
        
        return context

class PostCreateView(LoginRequiredMixin, CreateView):
    """Create a new blog post"""
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    success_url = reverse_lazy('home')
    
    def form_valid(self, form):
        # Set the author to current user
        form.instance.author = self.request.user
        
        # Save post and tags
        with transaction.atomic():
            post = form.save(commit=False)
            post.save()
            
            # Handle tags from form
            tags_input = form.cleaned_data.get('tags_input', '')
            if tags_input:
                tags = [tag.strip().lower() for tag in tags_input.split(',') if tag.strip()]
                post.tags.set(*tags)
            
            # Add success message
            messages.success(
                self.request, 
                f'Post "{post.title}" has been created successfully! '
                f'It is now {post.get_status_display().lower()}.'
            )
        
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New Post'
        context['submit_text'] = 'Create Post'
        return context

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update an existing blog post"""
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    context_object_name = 'post'
    
    def test_func(self):
        """Only post author can update"""
        post = self.get_object()
        return self.request.user == post.author
    
    def handle_no_permission(self):
        messages.error(self.request, "You don't have permission to edit this post.")
        return redirect('post_detail', pk=self.get_object().pk)
    
    def get_initial(self):
        """Set initial data including tags"""
        initial = super().get_initial()
        post = self.get_object()
        
        # Get current tags as comma-separated string
        tags = post.tags.all()
        if tags:
            initial['tags_input'] = ', '.join(tag.name for tag in tags)
        
        return initial
    
    def form_valid(self, form):
        # Update post
        with transaction.atomic():
            post = form.save()
            
            # Handle tags from form
            tags_input = form.cleaned_data.get('tags_input', '')
            if tags_input:
                tags = [tag.strip().lower() for tag in tags_input.split(',') if tag.strip()]
                post.tags.set(*tags)
            
            # Update timestamp
            post.updated_date = timezone.now()
            post.save()
            
            # Add success message
            messages.success(
                self.request, 
                f'Post "{post.title}" has been updated successfully!'
            )
        
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Post'
        context['submit_text'] = 'Update Post'
        return context

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a blog post"""
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('home')
    context_object_name = 'post'
    
    def test_func(self):
        """Only post author can delete"""
        post = self.get_object()
        return self.request.user == post.author
    
    def handle_no_permission(self):
        messages.error(self.request, "You don't have permission to delete this post.")
        return redirect('post_detail', pk=self.get_object().pk)
    
    def delete(self, request, *args, **kwargs):
        post = self.get_object()
        messages.success(request, f'Post "{post.title}" has been deleted successfully.')
        return super().delete(request, *args, **kwargs)

class DraftListView(LoginRequiredMixin, ListView):
    """Display user's draft posts"""
    model = Post
    template_name = 'blog/post_drafts.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        return Post.objects.filter(
            author=self.request.user,
            status='draft'
        ).order_by('-updated_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'My Drafts'
        return context

class UserPostListView(ListView):
    """Display all posts by a specific user"""
    model = Post
    template_name = 'blog/user_post_list.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        username = self.kwargs.get('username')
        self.author = get_object_or_404(User, username=username)
        return Post.objects.filter(
            author=self.author,
            status='published'
        ).order_by('-published_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author'] = self.author
        return context

@login_required
@require_POST
def post_like_view(request, pk):
    """Handle post likes"""
    post = get_object_or_404(Post, pk=pk)
    
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        liked = False
        message = 'Post unliked'
    else:
        post.likes.add(request.user)
        liked = True
        message = 'Post liked'
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': liked,
            'total_likes': post.total_likes,
            'message': message
        })
    
    messages.success(request, message)
    return redirect('post_detail', pk=post.pk)

@login_required
def add_comment(request, pk):
    """Add a comment to a post"""
    post = get_object_or_404(Post, pk=pk)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            
            # Handle parent comment (reply)
            parent_id = form.cleaned_data.get('parent_id')
            if parent_id:
                try:
                    parent_comment = Comment.objects.get(id=parent_id)
                    comment.parent = parent_comment
                except Comment.DoesNotExist:
                    pass
            
            # Auto-approve comments for post authors
            if comment.author == post.author:
                comment.approved = True
            
            comment.save()
            
            messages.success(request, 'Your comment has been submitted! ' + 
                            ('It is now visible.' if comment.approved else 'It will be visible after approval.'))
        else:
            for error in form.errors.values():
                messages.error(request, error)
    
    return redirect('post_detail', pk=post.pk)

@login_required
@require_POST
def delete_comment(request, pk):
    """Delete a comment"""
    comment = get_object_or_404(Comment, pk=pk)
    
    # Only allow deletion by comment author, post author, or staff
    if (request.user == comment.author or 
        request.user == comment.post.author or 
        request.user.is_staff):
        comment.delete()
        messages.success(request, 'Comment deleted successfully.')
    else:
        messages.error(request, "You don't have permission to delete this comment.")
    
    return redirect('post_detail', pk=comment.post.pk)

def search_posts(request):
    """Search functionality for posts"""
    form = SearchForm(request.GET or None)
    posts = Post.objects.filter(status='published')
    query = ''
    
    if form.is_valid():
        query = form.cleaned_data.get('query', '')
        if query:
            # Search in title, content, and tags
            posts = posts.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(tags__name__icontains=query)
            ).distinct().order_by('-published_date')
    
    # Pagination
    paginator = Paginator(posts, 10)  # Show 10 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'posts': page_obj,
        'query': query,
        'search_performed': bool(query),
        'total_results': posts.count(),
    }
    return render(request, 'blog/search_results.html', context)

def posts_by_tag(request, tag_slug):
    """View posts by specific tag"""
    tag = get_object_or_404(Tag, slug=tag_slug)
    posts = Post.objects.filter(
        status='published',
        tags__slug=tag_slug
    ).order_by('-published_date')
    
    # Pagination
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get related tags (tags that appear with this tag)
    post_ids = posts.values_list('id', flat=True)
    related_tags = Tag.objects.filter(
        blog_post__id__in=post_ids
    ).exclude(slug=tag_slug).annotate(
        num_posts=models.Count('taggit_taggeditem_items')
    ).order_by('-num_posts')[:10]
    
    context = {
        'tag': tag,
        'posts': page_obj,
        'related_tags': related_tags,
        'total_posts': posts.count(),
    }
    return render(request, 'blog/posts_by_tag.html', context)

def tag_cloud(request):
    """Display all tags as a tag cloud"""
    tags = Tag.objects.all().annotate(
        num_posts=models.Count('taggit_taggeditem_items')
    ).order_by('-num_posts')
    
    # Calculate tag size for cloud display
    if tags:
        max_count = tags[0].num_posts
        min_count = tags.last().num_posts
        for tag in tags:
            if max_count != min_count:
                size = 10 + ((tag.num_posts - min_count) / (max_count - min_count)) * 20
            else:
                size = 15
            tag.font_size = f"{size}px"
    
    context = {
        'tags': tags,
    }
    return render(request, 'blog/tag_cloud.html', context)

@login_required
def custom_logout_view(request):
    """Custom logout view with confirmation message"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')

class ProfileView(LoginRequiredMixin, TemplateView):
    """User profile view"""
    template_name = 'blog/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['profile'] = user.profile
        context['user_posts'] = Post.objects.filter(author=user).order_by('-published_date')[:5]
        context['user_comments'] = Comment.objects.filter(author=user).order_by('-created_date')[:5]
        return context

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Update user profile"""
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'blog/profile_edit.html'
    success_url = reverse_lazy('profile')
    
    def get_object(self):
        return self.request.user.profile
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)

@login_required
def change_password_view(request):
    """Change password view"""
    if request.method == 'POST':
        form = PasswordChangeCustomForm(request.user, request.POST)
        if form.is_valid():
            user = request.user
            new_password = form.cleaned_data['new_password1']
            user.set_password(new_password)
            user.save()
            
            # Re-authenticate user with new password
            login(request, user)
            messages.success(request, 'Your password has been changed successfully!')
            return redirect('profile')
    else:
        form = PasswordChangeCustomForm(request.user)
    
    return render(request, 'blog/change_password.html', {'form': form})

class UserPostsView(LoginRequiredMixin, ListView):
    """View all posts by the current user"""
    model = Post
    template_name = 'blog/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        return Post.objects.filter(author=self.request.user).order_by('-published_date')

class UserCommentsView(LoginRequiredMixin, ListView):
    """View all comments by the current user"""
    model = Comment
    template_name = 'blog/user_comments.html'
    context_object_name = 'comments'
    paginate_by = 10
    
    def get_queryset(self):
        return Comment.objects.filter(author=self.request.user).order_by('-created_date')

@login_required
def delete_account_view(request):
    """Delete user account"""
    if request.method == 'POST':
        # Verify password
        password = request.POST.get('password')
        if request.user.check_password(password):
            user = request.user
            logout(request)
            user.delete()
            messages.success(request, 'Your account has been deleted successfully.')
            return redirect('home')
        else:
            messages.error(request, 'Incorrect password. Account deletion failed.')
    

    return render(request, 'blog/delete_account.html')

class CommentCreateView(LoginRequiredMixin, CreateView):
    """Create a new comment on a post"""
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment_form.html'
    
    def form_valid(self, form):
        # Get the post from URL parameter
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, pk=post_id)
        
        # Set the comment author and post
        form.instance.author = self.request.user
        form.instance.post = post
        
        # Save the comment
        response = super().form_valid(form)
        
        # Add success message
        messages.success(self.request, 'Your comment has been added successfully!')
        
        return response
    
    def get_success_url(self):
        # Redirect back to the post detail page
        post_id = self.kwargs.get('post_id')
        return reverse_lazy('post_detail', kwargs={'pk': post_id})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post_id = self.kwargs.get('post_id')
        context['post'] = get_object_or_404(Post, pk=post_id)
        return context

class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update an existing comment"""
    model = Comment
    form_class = CommentEditForm
    template_name = 'blog/comment_edit.html'
    context_object_name = 'comment'
    
    def test_func(self):
        """Only comment author can update"""
        comment = self.get_object()
        return self.request.user == comment.author
    
    def handle_no_permission(self):
        """Handle unauthorized access"""
        comment = self.get_object()
        messages.error(self.request, "You don't have permission to edit this comment.")
        return redirect('post_detail', pk=comment.post.pk)
    
    def form_valid(self, form):
        # Mark that the comment has been edited
        form.instance.is_edited = True
        
        # Save and show success message
        response = super().form_valid(form)
        messages.success(self.request, 'Comment updated successfully!')
        
        return response
    
    def get_success_url(self):
        # Redirect back to the post
        return reverse_lazy('post_detail', kwargs={'pk': self.object.post.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.object.post
        return context

class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a comment"""
    model = Comment
    template_name = 'blog/comment_confirm_delete.html'
    context_object_name = 'comment'
    
    def test_func(self):
        """Only comment author or post author can delete"""
        comment = self.get_object()
        return (self.request.user == comment.author or 
                self.request.user == comment.post.author or
                self.request.user.is_staff)
    
    def handle_no_permission(self):
        """Handle unauthorized access"""
        comment = self.get_object()
        messages.error(self.request, "You don't have permission to delete this comment.")
        return redirect('post_detail', pk=comment.post.pk)
    
    def delete(self, request, *args, **kwargs):
        """Override delete to add success message"""
        messages.success(request, 'Comment deleted successfully!')
        return super().delete(request, *args, **kwargs)
    
    def get_success_url(self):
        # Redirect back to the post
        return reverse_lazy('post_detail', kwargs={'pk': self.object.post.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.object.post
        return context
