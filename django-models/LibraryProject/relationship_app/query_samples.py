# relationship_app/query_samples.py
import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from relationship_app.models import Author, Book, Library, Librarian

def demonstrate_relationships():
    print("=" * 60)
    print("DEMONSTRATING DJANGO MODEL RELATIONSHIPS")
    print("=" * 60)
    
    # 1. ForeignKey: Query all books by a specific author
    print("\n1. FOREIGNKEY RELATIONSHIP")
    print("-" * 30)
    
    try:
        author = Author.objects.get(name="J.K. Rowling")
        print(f"Author: {author.name}")
        
        books_by_author = author.books.all()
        print(f"Books by {author.name}:")
        for book in books_by_author:
            print(f"  - {book.title}")
    except Author.DoesNotExist:
        print("Author 'J.K. Rowling' not found. Run populate_sample_data.py first.")
    
    # 2. ManyToMany: List all books in a library - USING THE REQUIRED QUERY
    print("\n2. MANYTOMANY RELATIONSHIP")
    print("-" * 30)
    
    try:
        # THIS IS THE SPECIFIC QUERY YOU NEED: Library.objects.get(name=library_name)
        library_name = "Central Library"
        library = Library.objects.get(name=library_name)  # ← THIS LINE IS REQUIRED
        print(f"Library: {library.name}")
        
        books_in_library = library.books.all()
        print(f"Books in {library.name}:")
        for book in books_in_library:
            print(f"  - {book.title} (by {book.author.name})")
    except Library.DoesNotExist:
        print(f"Library '{library_name}' not found. Run populate_sample_data.py first.")
    
    # 3. OneToOne: Retrieve the librarian for a library
    print("\n3. ONETOONE RELATIONSHIP")
    print("-" * 30)
    
    try:
        library_name = "Central Library"
        library = Library.objects.get(name=library_name)  # Using the same pattern
        librarian = library.librarian
        print(f"Library: {library.name}")
        print(f"Librarian: {librarian.name}")
    except Library.DoesNotExist:
        print(f"Library '{library_name}' not found.")
    except Librarian.DoesNotExist:
        print(f"No librarian assigned to {library_name}")
    
    # 4. Additional demonstration with different library names
    print("\n4. QUERYING DIFFERENT LIBRARIES")
    print("-" * 30)
    
    library_names = ["Central Library", "City Public Library"]
    for library_name in library_names:
        try:
            library = Library.objects.get(name=library_name)  # ← USING THE REQUIRED QUERY
            books_count = library.books.count()
            print(f"📚 {library.name}: {books_count} books available")
        except Library.DoesNotExist:
            print(f"❌ Library '{library_name}' not found")

if __name__ == "__main__":
    demonstrate_relationships()
