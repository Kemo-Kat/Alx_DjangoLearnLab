# relationship_app/query_samples.py (Super Explicit Version)
import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from relationship_app.models import Author, Book, Library, Librarian

def demonstrate_required_queries():
    print("=" * 60)
    print("REQUIRED QUERY PATTERNS DEMONSTRATION")
    print("=" * 60)
    
    # REQUIRED QUERY 1: Author.objects.get(name=author_name)
    print("\n🔹 REQUIRED QUERY: Author.objects.get(name=author_name)")
    print("-" * 50)
    author_name = "J.K. Rowling"
    try:
        author = Author.objects.get(name=author_name)  # ← REQUIRED QUERY
        print(f"✅ Found author: {author.name}")
    except Author.DoesNotExist:
        print(f"❌ Author '{author_name}' not found")
        return
    
    # REQUIRED QUERY 2: objects.filter(author=author)
    print("\n🔹 REQUIRED QUERY: objects.filter(author=author)")
    print("-" * 50)
    filtered_books = Book.objects.filter(author=author)  # ← REQUIRED QUERY
    print(f"Books by {author.name} (using filter):")
    for book in filtered_books:
        print(f"  📖 {book.title}")
    
    # REQUIRED QUERY 3: Library.objects.get(name=library_name)
    print("\n🔹 REQUIRED QUERY: Library.objects.get(name=library_name)")
    print("-" * 50)
    library_name = "Central Library"
    try:
        library = Library.objects.get(name=library_name)  # ← REQUIRED QUERY
        print(f"✅ Found library: {library.name}")
        
        # Show books in library
        books_in_library = library.books.all()
        print(f"Books in {library.name}:")
        for book in books_in_library:
            print(f"  📚 {book.title}")
    except Library.DoesNotExist:
        print(f"❌ Library '{library_name}' not found")
    
    # OneToOne query demonstration
    print("\n🔹 ONE-TO-ONE RELATIONSHIP QUERY")
    print("-" * 50)
    try:
        library = Library.objects.get(name=library_name)
        librarian = library.librarian  # OneToOne access
        print(f"Librarian for {library.name}: {librarian.name}")
    except (Library.DoesNotExist, Librarian.DoesNotExist):
        print("Library or Librarian not found")

if __name__ == "__main__":
    demonstrate_required_queries()
