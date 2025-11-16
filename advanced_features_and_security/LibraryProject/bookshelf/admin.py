from django.contrib import admin
from .models import Book
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    """
    Admin interface for the CustomUser model.
    """
    model = CustomUser
    list_display = ('email', 'first_name', 'last_name', 'date_of_birth', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {
            'fields': (
                'first_name', 
                'last_name', 
                'date_of_birth', 
                'profile_photo'
            )
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 
                'first_name', 
                'last_name', 
                'date_of_birth',
                'profile_photo',
                'password1', 
                'password2', 
                'is_staff', 
                'is_active'
            ),
        }),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

# Register the custom user model
admin.site.register(CustomUser, CustomUserAdmin)










# Register your models here.
admin.site.register(Book)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = [
        'title', 
        'author', 
        'publication_year', 
        'is_available',
        'created_at'
    ]
    
    # Make title clickable for editing
    list_display_links = ['title']
    
    # Enable editing boolean fields directly from list view
    list_editable = ['is_available']
    
    # Filters for the right sidebar
    list_filter = [
        'publication_year',
        'author',
        'is_available',
        'created_at'
    ]
    
    # Search functionality
    search_fields = [
        'title',
        'author',
        'description',
        'isbn'
    ]
    
    # Date-based hierarchy navigation
    date_hierarchy = 'created_at'
    
    # Fields to display in the detail/edit form
    fieldsets = [
        ('Basic Information', {
            'fields': [
                'title',
                'author',
                'publication_year',
                'isbn'
            ]
        }),
        ('Content Details', {
            'fields': [
                'description',
                'genre',
                'page_count'
            ],
            'classes': ['wide']
        }),
        ('Availability', {
            'fields': ['is_available'],
            'classes': ['collapse']
        })
    ]
    
    # Configuration for the add form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('title', 'author', 'publication_year', 'isbn'),
        }),
    )
    
    # Read-only fields
    readonly_fields = ['created_at', 'updated_at']
    
    # Pagination
    list_per_page = 25
    
    # Actions
    actions = ['mark_as_available', 'mark_as_unavailable']
    
    def mark_as_available(self, request, queryset):
        """Custom admin action to mark books as available"""
        updated = queryset.update(is_available=True)
        self.message_user(request, f'{updated} books marked as available.')
    
    def mark_as_unavailable(self, request, queryset):
        """Custom admin action to mark books as unavailable"""
        updated = queryset.update(is_available=False)
        self.message_user(request, f'{updated} books marked as unavailable.')
    
    mark_as_available.short_description = "Mark selected books as available"
    mark_as_unavailable.short_description = "Mark selected books as unavailable"
    