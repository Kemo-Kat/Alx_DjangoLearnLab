from .forms import ExampleForm
from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib import messages
from .models import Book
from .forms import BookForm
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.db import connection
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils.html import escape
from .models import SecureUser
from .forms import SecureUserForm, SearchForm
import json
import logging

logger = logging.getLogger(__name__)

@csrf_protect  # Ensures CSRF protection for this view
@require_http_methods(["GET", "POST"])  # Restrict allowed HTTP methods
def create_user(request):
    """
    Secure view for creating users with proper input validation and CSRF protection.
    Uses Django ORM to prevent SQL injection.
    """
    if request.method == 'POST':
        form = SecureUserForm(request.POST)
        
        if form.is_valid():
            try:
                # Safe ORM usage - Django handles parameterization automatically
                user = form.save()
                messages.success(request, f"User {escape(user.name)} created successfully!")
                return redirect('user_list')
            except Exception as e:
                # Log error without exposing sensitive information
                logger.error(f"Error creating user: {str(e)}")
                messages.error(request, "An error occurred while creating the user. Please try again.")
        else:
            # Form validation failed - errors are automatically handled
            messages.error(request, "Please correct the errors below.")
    else:
        form = SecureUserForm()
    
    return render(request, 'secure_app/user_form.html', {'form': form})

@require_http_methods(["GET"])
def user_list(request):
    """
    Secure view for listing users with safe search functionality.
    Uses Django ORM to prevent SQL injection in search queries.
    """
    users = SecureUser.objects.all().order_by('-created_at')
    search_form = SearchForm()
    query = None
    
    # Safe search implementation using Django ORM
    if 'q' in request.GET:
        search_form = SearchForm(request.GET)
        if search_form.is_valid():
            query = search_form.cleaned_data['query']
            # Using Q objects for safe ORM-based search
            users = users.filter(
                Q(name__icontains=query) | 
                Q(email__icontains=query) | 
                Q(bio__icontains=query)
            )
    
    # Pagination for performance and security
    paginator = Paginator(users, 10)  # Show 10 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'query': query,
    }
    
    return render(request, 'secure_app/user_list.html', context)

@csrf_protect
@require_http_methods(["GET", "POST"])
def update_user(request, user_id):
    """
    Secure view for updating user information.
    Uses get_object_or_404 for safe object retrieval.
    """
    # Safe object retrieval - prevents exposure of non-existent objects
    user = get_object_or_404(SecureUser, id=user_id)
    
    if request.method == 'POST':
        form = SecureUserForm(request.POST, instance=user)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, f"User {escape(user.name)} updated successfully!")
                return redirect('user_list')
            except Exception as e:
                logger.error(f"Error updating user {user_id}: {str(e)}")
                messages.error(request, "An error occurred while updating the user.")
    else:
        form = SecureUserForm(instance=user)
    
    return render(request, 'secure_app/user_form.html', {'form': form, 'user': user})

@csrf_protect
@require_http_methods(["POST"])  # Only allow POST for deletion
def delete_user(request, user_id):
    """
    Secure user deletion with CSRF protection and safe object retrieval.
    """
    if request.method == 'POST':
        user = get_object_or_404(SecureUser, id=user_id)
        user_name = escape(user.name)
        
        try:
            user.delete()
            messages.success(request, f"User {user_name} deleted successfully!")
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {str(e)}")
            messages.error(request, "An error occurred while deleting the user.")
    
    return redirect('user_list')

@csrf_protect
@require_http_methods(["POST"])
def secure_ajax_search(request):
    """
    Secure AJAX endpoint for user search with CSRF protection and input validation.
    """
    try:
        # Parse JSON data safely
        data = json.loads(request.body)
        search_form = SearchForm(data)
        
        if search_form.is_valid():
            query = search_form.cleaned_data['query']
            
            # Safe ORM-based search
            users = SecureUser.objects.filter(
                Q(name__icontains=query) | 
                Q(email__icontains=query)
            ).values('id', 'name', 'email')[:10]  # Limit results for security
            
            # Sanitize output data
            safe_users = []
            for user in users:
                safe_users.append({
                    'id': user['id'],
                    'name': escape(user['name']),
                    'email': escape(user['email'])
                })
            
            return JsonResponse({'users': safe_users})
        else:
            return JsonResponse({'error': 'Invalid search query'}, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"AJAX search error: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

# DANGEROUS EXAMPLE - WHAT NOT TO DO (for educational purposes)
def unsafe_search(request):
    """
    UNSAFE: Example of vulnerable code that allows SQL injection.
    This is for demonstration purposes only - DO NOT USE in production.
    """
    query = request.GET.get('q', '')
    
    # VULNERABLE: Direct string formatting in SQL query
    unsafe_sql = f"SELECT * FROM secure_users WHERE name LIKE '%{query}%' OR email LIKE '%{query}%'"
    
    # This is extremely dangerous and allows SQL injection
    with connection.cursor() as cursor:
        cursor.execute(unsafe_sql)  # VULNERABLE TO SQL INJECTION
        results = cursor.fetchall()
    
    return JsonResponse({'results': results})

def safe_search_alternative(request):
    """
    SAFE: Proper way to execute raw SQL queries with parameterization.
    """
    query = request.GET.get('q', '')
    
    # SAFE: Parameterized SQL query
    safe_sql = "SELECT * FROM secure_users WHERE name LIKE %s OR email LIKE %s"
    params = [f'%{query}%', f'%{query}%']
    
    with connection.cursor() as cursor:
        cursor.execute(safe_sql, params)  # SAFE: Parameters are properly escaped
        results = cursor.fetchall()
    
    return JsonResponse({'results': results})



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

