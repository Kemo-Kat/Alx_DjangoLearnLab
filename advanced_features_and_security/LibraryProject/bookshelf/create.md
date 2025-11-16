# CREATE Operation

## Command:
```python
import os
import django
import sys

# Setup Django environment
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LibraryProject.settings')
django.setup()

from bookshelf.models import Book

# CREATE a new Book instance
book = Book.objects.create(
    title="1984",
    author="George Orwell", 
    publication_year=1949
)

# Display the created book details
print(f"Book created successfully!")
print(f"ID: {book.id}")
print(f"Title: {book.title}")
print(f"Author: {book.author}")
print(f"Publication Year: {book.publication_year}")