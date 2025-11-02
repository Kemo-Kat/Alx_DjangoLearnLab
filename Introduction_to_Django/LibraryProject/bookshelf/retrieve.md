# RETRIEVE Operation

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

# RETRIEVE the book we created
book = Book.objects.get(title="1984")

# Display all attributes
print("=== Book Details ===")
print(f"ID: {book.id}")
print(f"Title: {book.title}")
print(f"Author: {book.author}")
print(f"Publication Year: {book.publication_year}")

# Alternative: Retrieve all books
print("\n=== All Books in Database ===")
all_books = Book.objects.all()
print(f"Total books: {all_books.count()}")
for book in all_books:
    print(f"- {book.title} by {book.author}")