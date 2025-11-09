# relationship_app/views.py (temporary alternative)
from django.shortcuts import render
from django.views.generic import ListView
from .models import Book

# Function-based view
def list_books(request):
    books = Book.objects.all().select_related('author')
    return render(request, 'relationship_app/list_books.html', {'books': books})

# Alternative class-based view using Book model
class BookListView(ListView):
    model = Book
    template_name = 'relationship_app/book_list.html'
    context_object_name = 'books'
