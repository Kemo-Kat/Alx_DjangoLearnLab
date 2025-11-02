# DELETE Operation

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

# Check current state before deletion
print("=== Before Deletion ===")
all_books_before = Book.objects.all()
print(f"Books in database: {all_books_before.count()}")
for book in all_books_before:
    print(f"- {book.title} by {book.author}")

# DELETE the book
book_to_delete = Book.objects.get(title="Nineteen Eighty-Four")
book_to_delete.delete()

# Verify deletion
print("\n=== After Deletion ===")
all_books_after = Book.objects.all()
print(f"Books in database: {all_books_after.count()}")

# Try to retrieve the deleted book (should raise error)
print("\n=== Verification ===")
try:
    deleted_book = Book.objects.get(title="Nineteen Eighty-Four")
    print(f"ERROR: Book still exists: {deleted_book}")
except Book.DoesNotExist:
    print("SUCCESS: Book successfully deleted - no longer exists in database")