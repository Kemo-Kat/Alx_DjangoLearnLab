# relationship_app/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from .models import views
from .views import list_books

app_name = 'relationship_app'
app_name = 'accounts'

urlpatterns = [
    # Function-based view URL - lists all books
    path('books/', views.list_books, name='list_books'),
    
    # Class-based view URL - displays specific library details
    path('library/<int:pk>/', views.LibraryDetailView.as_view(), name='library_detail'),
        path('login/', auth_views.LoginView.as_view(template_name='relationship_app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='relationship_app/logout.html'), name='logout'),
    path('register/', views.register, name='register'),

    path('admin/', admin.site.urls),

    path('relationship/', include('relationship_app.urls')),
    path('admin/', views.admin_view, name='admin_view'),
    path('librarian/', views.librarian_view, name='librarian_view'),
    path('member/', views.member_view, name='member_view'),
        # Public URLs
    path('', views.book_list, name='book_list'),
    path('book/<int:pk>/', views.book_detail, name='book_detail'),
    
    # Secured URLs with custom permissions
    path('book/add/', views.book_create, name='book_create'),
    path('book/<int:pk>/edit/', views.book_update, name='book_update'),
    path('book/<int:pk>/delete/', views.book_delete, name='book_delete'),
    
    # Management dashboard
    path('dashboard/', views.book_management_dashboard, name='book_dashboard'),

]





