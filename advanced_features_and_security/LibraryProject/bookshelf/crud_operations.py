# crud_operations.py
import os
import django
import sys

# Add the project directory to the Python path
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_path)

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LibraryProject.settings')
django.setup()

from bookshelf.models import Book

print("=== DJANGO CRUD OPERATIONS ===")

# CREATE Operation
print("\n1. CREATE: Creating a new book...")
book = Book.objects.create(
    title="1984", 
    author="George Orwell", 
    publication_year=1949
)
print(f"✓ Created book: {book.title} (ID: {book.id})")

# RETRIEVE Operation  
print("\n2. RETRIEVE: Retrieving the book...")
retrieved_book = Book.objects.get(id=book.id)
print(f"✓ Retrieved: {retrieved_book.title} by {retrieved_book.author}, {retrieved_book.publication_year}")

# UPDATE Operation
print("\n3. UPDATE: Updating the book title...")
retrieved_book.title = "Nineteen Eighty-Four"
retrieved_book.save()
print(f"✓ Updated title to: {retrieved_book.title}")

# DELETE Operation
print("\n4. DELETE: Deleting the book...")
retrieved_book.delete()
print("✓ Book deleted")

# Final verification
remaining = Book.objects.all().count()
print(f"\n✓ Final check: {remaining} books in database")
print("=== ALL OPERATIONS COMPLETED ===")