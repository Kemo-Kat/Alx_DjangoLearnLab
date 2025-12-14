from rest_framework import serializers
from .models import Post, Comment

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'created_at', 'updated_at']
        read_only_fields = ['author', 'post']

class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    comments = CommentSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    user_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'author', 'title', 'content', 'created_at', 'updated_at', 
                  'comments', 'likes_count', 'user_liked']
        read_only_fields = ['author']
    
    def get_likes_count(self, obj):
        return obj.like_set.count()
    
    def get_user_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.like_set.filter(user=request.user).exists()
        return False
    
    class Meta:
        model = Post
        fields = ['id', 'author', 'title', 'content', 'created_at', 'updated_at', 'comments']
        read_only_fields = ['author']