# relationship_app/views.py
from django.shortcuts import render
from django.views.generic.detail import DetailView
from .models import Library, Book  # Add Library to import

# Function-based view to list all books
def list_books(request):
    books = Book.objects.all().select_related('author')
    return render(request, 'relationship_app/list_books.html', {'books': books})

# Class-based view to display library details
class LibraryDetailView(DetailView):
    model = Library  # This requires the Library import
    template_name = 'relationship_app/library_detail.html'  # Add the template name
    context_object_name = 'library'  # Add context object name
    
    def get_queryset(self):
        return Library.objects.prefetch_related('books__author')


