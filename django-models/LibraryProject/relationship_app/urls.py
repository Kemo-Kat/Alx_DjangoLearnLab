from django.urls import path
from django.contrib.auth import views as auth_views
from .models import views
from .views import list_books
app_name = 'relationship_app'

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

]
