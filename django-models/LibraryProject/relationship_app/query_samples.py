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
    print("=" + 60)
    
    # Define names for queries
    author_name = "J.K. Rowling"
    library_name = "Central Library"
    
    # 1. ForeignKey Relationship: Query all books by a specific author
    print("\n1. FOREIGNKEY RELATIONSHIP")
    print("-" * 30)
    
    try:
        # REQUIRED QUERY: Author.objects.get(name=author_name)
        author = Author.objects.get(name=author_name)
        print(f"Author: {author.name}")
        
        # Method 1: Using related_name (author.books.all())
        books_by_author_related = author.books.all()
        print(f"Books by {author.name} (using related_name):")
        for book in books_by_author_related:
            print(f"  - {book.title}")
        
        # Method 2: REQUIRED QUERY: objects.filter(author=author)
        books_by_author_filter = Book.objects.filter(author=author)
        print(f"\nBooks by {author.name} (using filter):")
        for book in books_by_author_filter:
            print(f"  - {book.title}")
            
    except Author.DoesNotExist:
        print(f"Author '{author_name}' not found. Run populate_sample_data.py first.")
    
    # 2. ManyToMany Relationship: List all books in a library
    print("\n2. MANYTOMANY RELATIONSHIP")
    print("-" * 30)
    
    try:
        # REQUIRED QUERY: Library.objects.get(name=library_name)
        library = Library.objects.get(name=library_name)
        print(f"Library: {library.name}")
        
        books_in_library = library.books.all()
        print(f"Books in {library.name}:")
        for book in books_in_library:
            print(f"  - {book.title} (by {book.author.name})")
    except Library.DoesNotExist:
        print(f"Library '{library_name}' not found. Run populate_sample_data.py first.")
    
    # 3. OneToOne Relationship: Retrieve the librarian for a library
    print("\n3. ONETOONE RELATIONSHIP")
    print("-" * 30)
    
    try:
        # REQUIRED QUERY: Library.objects.get(name=library_name)
        library = Library.objects.get(name=library_name)
        
        # Method 1: Using the OneToOne relationship directly
        librarian_direct = library.librarian
        print(f"Method 1 - Direct access:")
        print(f"  Library: {library.name}")
        print(f"  Librarian: {librarian_direct.name}")
        
        # Method 2: REQUIRED QUERY: Librarian.objects.get(library=library)
        librarian_query = Librarian.objects.get(library=library)
        print(f"\nMethod 2 - Using Librarian.objects.get(library=library):")
        print(f"  Library: {library.name}")
        print(f"  Librarian: {librarian_query.name}")
        
        # Method 3: REQUIRED QUERY: Librarian.objects.get(library__name=library_name)
        librarian_by_name = Librarian.objects.get(library__name=library_name)
        print(f"\nMethod 3 - Using Librarian.objects.get(library__name='{library_name}'):")
        print(f"  Library: {library.name}")
        print(f"  Librarian: {librarian_by_name.name}")
        
    except Library.DoesNotExist:
        print(f"Library '{library_name}' not found.")
    except Librarian.DoesNotExist:
        print(f"No librarian assigned to {library_name}")
    
    # 4. Additional Examples
    print("\n4. ADDITIONAL QUERY EXAMPLES")
    print("-" * 30)
    
    # Query different libraries and their librarians
    library_names = ["Central Library", "City Public Library"]
    for lib_name in library_names:
        try:
            library = Library.objects.get(name=lib_name)
            librarian = Librarian.objects.get(library=library)
            print(f"📚 {library.name} → 👨‍💼 {librarian.name}")
        except Library.DoesNotExist:
            print(f"❌ Library '{lib_name}' not found")
        except Librarian.DoesNotExist:
            print(f"❌ No librarian for '{lib_name}'")

if __name__ == "__main__":
    demonstrate_relationships()
