# UPDATE Operation

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

# RETRIEVE the book to update
book = Book.objects.get(title="1984")
print(f"Before update - Title: {book.title}")

# UPDATE the title
book.title = "Nineteen Eighty-Four"
book.save()

# Verify the update
updated_book = Book.objects.get(id=book.id)
print(f"After update - Title: {updated_book.title}")

# Display all current attributes
print("\n=== Updated Book Details ===")
print(f"ID: {updated_book.id}")
print(f"Title: {updated_book.title}")
print(f"Author: {updated_book.author}")
print(f"Publication Year: {updated_book.publication_year}")