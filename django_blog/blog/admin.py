from django.contrib import admin
from .models import Post, Comment, UserProfile
from django.utils.html import format_html
from taggit.models import Tag

# Register your models here.


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'published_date', 'view_count', 'like_count', 'comment_count')
    list_filter = ('status', 'published_date', 'author', 'tags')
    search_fields = ('title', 'content', 'excerpt', 'author__username')
    readonly_fields = ('views', 'published_date', 'updated_date', 'slug')
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'author', 'status')
        }),
        ('Content', {
            'fields': ('excerpt', 'content', 'image', 'image_caption')
        }),
        ('Metadata', {
            'fields': ('tags', 'views', 'published_date', 'updated_date')
        }),
    )
    filter_horizontal = ('tags', 'likes')
    date_hierarchy = 'published_date'
    ordering = ('-published_date',)
    
    def display_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])
    display_tags.short_description = 'Tags'

    def view_count(self, obj):
        return obj.views
    view_count.short_description = 'Views'
    
    def like_count(self, obj):
        return obj.total_likes
    like_count.short_description = 'Likes'
    
    def comment_count(self, obj):
        return obj.comments.count()
    comment_count.short_description = 'Comments'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post_preview', 'content_preview', 'created_date', 'approved', 'is_reply')
    list_filter = ('approved', 'created_date', 'post')
    search_fields = ('content', 'author__username', 'post__title')
    actions = ['approve_comments', 'disapprove_comments']
    readonly_fields = ('created_date', 'updated_date')
    
    def post_preview(self, obj):
        return format_html('<a href="{}">{}</a>', 
                          f'/admin/blog/post/{obj.post.id}/change/',
                          obj.post.title[:50])
    post_preview.short_description = 'Post'
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'
    
    def is_reply(self, obj):
        return bool(obj.parent)
    is_reply.boolean = True
    is_reply.short_description = 'Reply'
    
    def approve_comments(self, request, queryset):
        queryset.update(approved=True)
    approve_comments.short_description = "Approve selected comments"
    
    def disapprove_comments(self, request, queryset):
        queryset.update(approved=False)
    disapprove_comments.short_description = "Disapprove selected comments"

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'post_count', 'comment_count')
    search_fields = ('user__username', 'bio', 'location')
    readonly_fields = ('user',)
    
    def post_count(self, obj):
        return obj.user.blog_posts.count()
    post_count.short_description = 'Posts'
    
    def comment_count(self, obj):
        return obj.user.comment_set.count()
    comment_count.short_description = 'Comments'