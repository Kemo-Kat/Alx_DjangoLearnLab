# relationship_app/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Book, Library
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import permission_required, login_required, user_passes_test
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .forms import BookForm


def is_admin(user):
    return user.is_authenticated and hasattr(user, 'userprofile') and user.userprofile.role == 'Admin'

def is_librarian(user):
    return user.is_authenticated and hasattr(user, 'userprofile') and user.userprofile.role == 'Librarian'

def is_member(user):
    return user.is_authenticated and hasattr(user, 'userprofile') and user.userprofile.role == 'Member'

# Admin View - Only accessible to Admin role
@login_required
@user_passes_test(is_admin, login_url='/accounts/login/')
def admin_view(request):
    context = {
        'username': request.user.username,
        'role': request.user.userprofile.role if hasattr(request.user, 'userprofile') else 'No Role'
    }
    return render(request, 'relationship_app/admin_view.html', context)

# Librarian View - Only accessible to Librarian role
@login_required
@user_passes_test(is_librarian, login_url='/accounts/login/')
def librarian_view(request):
    context = {
        'username': request.user.username,
        'role': request.user.userprofile.role if hasattr(request.user, 'userprofile') else 'No Role'
    }
    return render(request, 'relationship_app/librarian_view.html', context)

# Member View - Only accessible to Member role
@login_required
@user_passes_test(is_member, login_url='/accounts/login/')
def member_view(request):
    context = {
        'username': request.user.username,
        'role': request.user.userprofile.role if hasattr(request.user, 'userprofile') else 'No Role'
    }
    return render(request, 'relationship_app/member_view.html', context)

# Function-based view to list all books
def list_books(request):
    books = Book.objects.all().select_related('author')
    return render(request, 'relationship_app/list_books.html', {'books': books})

# relationship_app/views.py (continued)
# Class-based view to display library details
class LibraryDetailView(DetailView):
    model = Library
    template_name = 'relationship_app/library_detail.html'
    context_object_name = 'library'
    
    def get_queryset(self):
        return Library.objects.prefetch_related('books__author')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'relationship_app/register.html', {'form': form})

# Example of a protected view
@login_required
def profile(request):
    return render(request, 'relationship_app/profile.html')

# View to list all books (public access)
def book_list(request):
    books = Book.objects.all()
    return render(request, 'relationship_app/book_list.html', {'books': books})

# View to show book details (public access)
def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'relationship_app/book_detail.html', {'book': book})

# Secured view for adding books - requires custom permission
@permission_required('relationship_app.can_add_book', raise_exception=True)
def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            book.created_by = request.user
            book.save()
            messages.success(request, 'Book created successfully!')
            return redirect('book_detail', pk=book.pk)
    else:
        form = BookForm()
    
    return render(request, 'relationship_app/book_form.html', {
        'form': form,
        'title': 'Add New Book'
    })

# Secured view for editing books - requires custom permission
@permission_required('relationship_app.can_change_book', raise_exception=True)
def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book updated successfully!')
            return redirect('book_detail', pk=book.pk)
    else:
        form = BookForm(instance=book)
    
    return render(request, 'relationship_app/book_form.html', {
        'form': form,
        'title': 'Edit Book',
        'book': book
    })

# Secured view for deleting books - requires custom permission
@permission_required('relationship_app.can_delete_book', raise_exception=True)
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Book deleted successfully!')
        return redirect('book_list')
    
    return render(request, 'relationship_app/book_confirm_delete.html', {'book': book})

# Optional: Dashboard view to show books with management options
@login_required
def book_management_dashboard(request):
    books = Book.objects.all()
    # Check what permissions the current user has
    can_add = request.user.has_perm('relationship_app.can_add_book')
    can_change = request.user.has_perm('relationship_app.can_change_book')
    can_delete = request.user.has_perm('relationship_app.can_delete_book')
    
    return render(request, 'relationship_app/book_dashboard.html', {
        'books': books,
        'can_add': can_add,
        'can_change': can_change,
        'can_delete': can_delete,
    })
