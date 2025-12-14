from django.shortcuts import render
from rest_framework import viewsets, permissions, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Like
from notifications.models import Notification
from rest_framework import generics

# Create your views here.

class LikeView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        ["generics.get_object_or_404(Post, pk=pk)"]
        
        # Check if already liked
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        
        if not created:
            return Response({'error': 'You already liked this post'}, status=400)
        
        # Create notification if user likes someone else's post
        if post.author != request.user:
            Notification.objects.create(
                recipient=post.author,
                actor=request.user,
                verb="liked your post",
                target_post=post
            )
        
        return Response({'message': 'Post liked successfully'})
class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user

class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['title', 'content']
    
    def get_queryset(self):
        return Post.objects.all().order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    
    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        return Comment.objects.filter(post_id=post_id).order_by('created_at')
    
    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        post = Post.objects.get(id=post_id)
        comment = serializer.save(author=self.request.user, post_id=post_id)
        
        # Create notification if user comments on someone else's post
        if post.author != self.request.user:
            Notification.objects.create(
                recipient=post.author,
                actor=self.request.user,
                verb="commented on your post",
                target_post=post,
                target_comment=comment
            )



class PostViewSet(viewsets.ModelViewSet):
    # ... existing code ...
    
    @action(detail=False, methods=['get'])
    def feed(self, request):
        # Get users that the current user follows
        following_users = request.user.followers.all()
        
        # Get posts from followed users
        feed_posts = Post.objects.filter(author__in=following_users).order_by('-created_at')
        
        # Paginate results
        page = self.paginate_queryset(feed_posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(feed_posts, many=True)
        return Response(serializer.data)

class LikeView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        post = get_object_or_404(Post, id=pk)
        
        # Check if already liked
        if Like.objects.filter(user=request.user, post=post).exists():
            return Response({'error': 'You already liked this post'}, status=400)
        
        # Create like
        Like.objects.create(user=request.user, post=post)
        
        # Create notification if user likes someone else's post
        if post.author != request.user:
            Notification.objects.create(
                recipient=post.author,
                actor=request.user,
                verb="liked your post",
                target_post=post
            )
        
        return Response({'message': 'Post liked successfully'})

class UnlikeView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        post = get_object_or_404(Post, id=pk)
        
        try:
            like = Like.objects.get(user=request.user, post=post)
            like.delete()
            return Response({'message': 'Post unliked successfully'})
        except Like.DoesNotExist:

            return Response({'error': 'You have not liked this post'}, status=400)

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user

class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['title', 'content']
    
    def get_queryset(self):
        return Post.objects.all().order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    
    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        if post_id:
            return Comment.objects.filter(post_id=post_id).order_by('created_at')
        return Comment.objects.all().order_by('created_at')
    
    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        serializer.save(author=self.request.user, post_id=post_id)

class LikeView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        
        # Check if already liked
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        
        if not created:
            return Response({'error': 'You already liked this post'}, status=400)
        
        # Create notification if user likes someone else's post
        if post.author != request.user:
            Notification.objects.create(
                recipient=post.author,
                actor=request.user,
                verb="liked your post",
                target_post=post
            )
        
        return Response({'message': 'Post liked successfully'})


