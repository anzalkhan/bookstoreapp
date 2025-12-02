import os
import sys
from dotenv import load_dotenv
from models import db, User, Book

# Load environment variables
load_dotenv()

# Add parent directory to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def init_database():
    """Initialize the database with tables and sample data"""
    from flask import Flask
    
    app = Flask(__name__)
    
    # Database configuration
    db_user = os.getenv('DB_USER', 'root')
    db_password = os.getenv('DB_PASSWORD', '')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '3306')
    db_name = os.getenv('DB_NAME', 'bookstore')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    db.init_app(app)
    
    with app.app_context():
        # Drop all tables and recreate
        print("Dropping existing tables...")
        db.drop_all()
        
        print("Creating tables...")
        db.create_all()
        
        # Create default manager account
        print("Creating default manager account...")
        manager = User(
            username='admin',
            email='admin@bookstore.com',
            is_manager=True
        )
        manager.set_password('admin123')
        db.session.add(manager)
        
        # Add sample books
        print("Adding sample books...")
        sample_books = [
            {
                'title': 'To Kill a Mockingbird',
                'author': 'Harper Lee',
                'buy_price': 15.99,
                'rent_price': 3.99
            },
            {
                'title': '1984',
                'author': 'George Orwell',
                'buy_price': 14.99,
                'rent_price': 3.49
            },
            {
                'title': 'The Great Gatsby',
                'author': 'F. Scott Fitzgerald',
                'buy_price': 12.99,
                'rent_price': 2.99
            },
            {
                'title': 'Pride and Prejudice',
                'author': 'Jane Austen',
                'buy_price': 13.99,
                'rent_price': 3.29
            },
            {
                'title': 'The Catcher in the Rye',
                'author': 'J.D. Salinger',
                'buy_price': 14.49,
                'rent_price': 3.49
            },
            {
                'title': 'Harry Potter and the Sorcerer\'s Stone',
                'author': 'J.K. Rowling',
                'buy_price': 19.99,
                'rent_price': 4.99
            },
            {
                'title': 'The Lord of the Rings',
                'author': 'J.R.R. Tolkien',
                'buy_price': 25.99,
                'rent_price': 5.99
            },
            {
                'title': 'The Hobbit',
                'author': 'J.R.R. Tolkien',
                'buy_price': 16.99,
                'rent_price': 3.99
            },
            {
                'title': 'Brave New World',
                'author': 'Aldous Huxley',
                'buy_price': 14.99,
                'rent_price': 3.49
            },
            {
                'title': 'The Chronicles of Narnia',
                'author': 'C.S. Lewis',
                'buy_price': 22.99,
                'rent_price': 5.49
            }
        ]
        
        for book_data in sample_books:
            book = Book(**book_data)
            db.session.add(book)
        
        db.session.commit()
        print("Database initialized successfully!")
        print("\nDefault Manager Account:")
        print("  Username: admin")
        print("  Password: admin123")
        print("\nPlease change this password after first login!")


if __name__ == '__main__':
    init_database()
