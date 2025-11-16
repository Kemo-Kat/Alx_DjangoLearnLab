from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib import messages
from .models import Book
from .forms import BookForm

# View to list all books (public access)
def book_list(request):
    books = Book.objects.all()
    return render(request, 'bookshelf/book_list.html', {'books': books})

# View to show book details (public access)
def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'bookshelf/book_detail.html', {'book': book})

# Secured view for adding books - requires can_create permission
@permission_required('bookshelf.can_create', raise_exception=True)
def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            book.created_by = request.user
            book.save()
            messages.success(request, 'Book created successfully!')
            return redirect('bookshelf:book_detail', pk=book.pk)
    else:
        form = BookForm()
    
    return render(request, 'bookshelf/book_form.html', {
        'form': form,
        'title': 'Add New Book'
    })

# View for editing books (using can_create permission for editing as well)
@permission_required('bookshelf.can_create', raise_exception=True)
def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book updated successfully!')
            return redirect('bookshelf:book_detail', pk=book.pk)
    else:
        form = BookForm(instance=book)
    
    return render(request, 'bookshelf/book_form.html', {
        'form': form,
        'title': 'Edit Book',
        'book': book
    })

# Secured view for deleting books - requires can_delete permission
@permission_required('bookshelf.can_delete', raise_exception=True)
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Book deleted successfully!')
        return redirect('bookshelf:book_list')
    
    return render(request, 'bookshelf/book_confirm_delete.html', {'book': book})

# Dashboard view to show books with management options
@login_required
def book_management_dashboard(request):
    books = Book.objects.all()
    # Check what permissions the current user has
    can_create = request.user.has_perm('bookshelf.can_create')
    can_delete = request.user.has_perm('bookshelf.can_delete')
    
    return render(request, 'bookshelf/book_dashboard.html', {
        'books': books,
        'can_create': can_create,
        'can_delete': can_delete,
    })
# Create your views here.

