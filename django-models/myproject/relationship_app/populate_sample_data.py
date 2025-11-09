# relationship_app/populate_sample_data.py
import os
import django
import sys

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project_name.settings')
django.setup()

from .models import Author, Book, Library, Librarian

def create_sample_data():
    # Create authors
    author1 = Author.objects.create(name="J.K. Rowling")
    author2 = Author.objects.create(name="George R.R. Martin")
    author3 = Author.objects.create(name="J.R.R. Tolkien")
    
    # Create books
    book1 = Book.objects.create(title="Harry Potter and the Philosopher's Stone", author=author1)
    book2 = Book.objects.create(title="Harry Potter and the Chamber of Secrets", author=author1)
    book3 = Book.objects.create(title="A Game of Thrones", author=author2)
    book4 = Book.objects.create(title="A Clash of Kings", author=author2)
    book5 = Book.objects.create(title="The Hobbit", author=author3)
    book6 = Book.objects.create(title="The Lord of the Rings", author=author3)
    
    # Create libraries
    library1 = Library.objects.create(name="Central Library")
    library2 = Library.objects.create(name="City Public Library")
    
    # Add books to libraries (ManyToMany relationship)
    library1.books.add(book1, book2, book5)
    library2.books.add(book3, book4, book6)
    
    # Create librarians (OneToOne relationship)
    librarian1 = Librarian.objects.create(name="Alice Johnson", library=library1)
    librarian2 = Librarian.objects.create(name="Bob Smith", library=library2)
    
    print("Sample data created successfully!")
    print(f"Authors: {Author.objects.count()}")
    print(f"Books: {Book.objects.count()}")
    print(f"Libraries: {Library.objects.count()}")
    print(f"Librarians: {Librarian.objects.count()}")

if __name__ == "__main__":
    create_sample_data()