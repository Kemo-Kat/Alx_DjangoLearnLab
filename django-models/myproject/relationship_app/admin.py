# relationship_app/admin.py
from django.contrib import admin
from .models import Author, Book, Library, Librarian

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'author']
    list_filter = ['author']
    search_fields = ['title']

@admin.register(Library)
class LibraryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    filter_horizontal = ['books']  # Better interface for ManyToMany
    search_fields = ['name']

@admin.register(Librarian)
class LibrarianAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'library']
    search_fields = ['name', 'library__name']