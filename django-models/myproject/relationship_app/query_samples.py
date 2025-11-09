# relationship_app/query_samples.py
import os
import django
import sys

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project_name.settings')
django.setup()

from .models import Author, Book, Library, Librarian

def demonstrate_relationships():
    print("=" * 60)
    print("DEMONSTRATING DJANGO MODEL RELATIONSHIPS")
    print("=" * 60)
    
    # 1. ForeignKey Relationship: Query all books by a specific author
    print("\n1. FOREIGNKEY RELATIONSHIP")
    print("-" * 30)
    
    # Get an author
    try:
        author = Author.objects.get(name="J.K. Rowling")
        print(f"Author: {author.name}")
        
        # Query all books by this author (using related_name='books')
        books_by_author = author.books.all()
        print(f"Books by {author.name}:")
        for book in books_by_author:
            print(f"  - {book.title}")
    except Author.DoesNotExist:
        print("Author 'J.K. Rowling' not found. Please run populate_sample_data.py first.")
    
    # 2. ManyToMany Relationship: List all books in a library
    print("\n2. MANYTOMANY RELATIONSHIP")
    print("-" * 30)
    
    try:
        library = Library.objects.get(name="Central Library")
        print(f"Library: {library.name}")
        
        # Query all books in this library
        books_in_library = library.books.all()
        print(f"Books in {library.name}:")
        for book in books_in_library:
            print(f"  - {book.title} (by {book.author.name})")
    except Library.DoesNotExist:
        print("Library 'Central Library' not found. Please run populate_sample_data.py first.")
    
    # 3. OneToOne Relationship: Retrieve the librarian for a library
    print("\n3. ONETOONE RELATIONSHIP")
    print("-" * 30)
    
    try:
        library = Library.objects.get(name="Central Library")
        
        # Retrieve the librarian for this library (using related_name='librarian')
        librarian = library.librarian
        print(f"Library: {library.name}")
        print(f"Librarian: {librarian.name}")
    except Library.DoesNotExist:
        print("Library 'Central Library' not found.")
    except Librarian.DoesNotExist:
        print(f"No librarian assigned to {library.name}")
    except AttributeError:
        print(f"No librarian relationship found for {library.name}")
    
    # Additional demonstration: Reverse relationships
    print("\n4. REVERSE RELATIONSHIPS")
    print("-" * 30)
    
    # From Book to Libraries (ManyToMany reverse)
    try:
        book = Book.objects.get(title="Harry Potter and the Philosopher's Stone")
        libraries_with_book = book.libraries.all()
        print(f"Book: {book.title}")
        print(f"Available in libraries:")
        for lib in libraries_with_book:
            print(f"  - {lib.name}")
    except Book.DoesNotExist:
        print("Book not found.")
    
    # From Librarian to Library (OneToOne reverse is automatic)
    try:
        librarian = Librarian.objects.get(name="Alice Johnson")
        print(f"\nLibrarian: {librarian.name}")
        print(f"Works at: {librarian.library.name}")
    except Librarian.DoesNotExist:
        print("Librarian not found.")

if __name__ == "__main__":
    demonstrate_relationships()