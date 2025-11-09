# relationship_app/urls.py
from django.urls import path
from .models import views
from .views import list_books

app_name = 'relationship_app'

urlpatterns = [
    # Function-based view URL - lists all books
    path('books/', views.list_books, name='list_books'),
    
    # Class-based view URL - displays specific library details
    path('library/<int:pk>/', views.LibraryDetailView.as_view(), name='library_detail'),

    path('admin/', admin.site.urls),
    
    path('relationship/', include('relationship_app.urls')),

]


