from flask import Flask, request, jsonify, session
from flask_cors import CORS
from dotenv import load_dotenv
import os
from models import db, bcrypt, User, Book, Order, OrderItem
from email_service import EmailService
from datetime import timedelta

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
db_user = os.getenv('DB_USER', 'root')
db_password = os.getenv('DB_PASSWORD', '')
db_host = os.getenv('DB_HOST', 'localhost')
db_port = os.getenv('DB_PORT', '3306')
db_name = os.getenv('DB_NAME', 'bookstore')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)
CORS(app, supports_credentials=True)

# Initialize email service
email_service = EmailService()


# Authentication decorator
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function


def manager_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        user = User.query.get(session['user_id'])
        if not user or not user.is_manager:
            return jsonify({'error': 'Manager access required'}), 403
        return f(*args, **kwargs)
    return decorated_function


# ==================== Authentication Routes ====================

@app.route('/api/register', methods=['POST'])
def register():
    """Register a new customer account"""
    data = request.get_json()
    
    # Validate required fields
    if not data.get('username') or not data.get('password') or not data.get('email'):
        return jsonify({'error': 'Username, password, and email are required'}), 400
    
    # Check if username already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    # Check if email already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    # Create new user
    user = User(
        username=data['username'],
        email=data['email'],
        is_manager=False
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': 'Registration successful',
        'user': user.to_dict()
    }), 201


@app.route('/api/login', methods=['POST'])
def login():
    """Login for both customers and managers"""
    data = request.get_json()
    
    if not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password are required'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    # Create session
    session.permanent = True
    session['user_id'] = user.id
    session['is_manager'] = user.is_manager
    
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict()
    }), 200


@app.route('/api/logout', methods=['POST'])
def logout():
    """Logout current user"""
    session.clear()
    return jsonify({'message': 'Logout successful'}), 200


@app.route('/api/session', methods=['GET'])
def check_session():
    """Check if user is logged in"""
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            return jsonify({
                'authenticated': True,
                'user': user.to_dict()
            }), 200
    
    return jsonify({'authenticated': False}), 200


# ==================== Book Routes ====================

@app.route('/api/books/search', methods=['GET'])
@login_required
def search_books():
    """Search books by title or author"""
    keyword = request.args.get('keyword', '')
    
    if not keyword:
        # Return all books if no keyword provided
        books = Book.query.all()
    else:
        # Search in title and author
        books = Book.query.filter(
            db.or_(
                Book.title.ilike(f'%{keyword}%'),
                Book.author.ilike(f'%{keyword}%')
            )
        ).all()
    
    return jsonify({
        'books': [book.to_dict() for book in books]
    }), 200


@app.route('/api/books', methods=['POST'])
@manager_required
def add_book():
    """Add a new book (Manager only)"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['title', 'author', 'buy_price', 'rent_price']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    book = Book(
        title=data['title'],
        author=data['author'],
        buy_price=float(data['buy_price']),
        rent_price=float(data['rent_price']),
        available_for_purchase=data.get('available_for_purchase', True),
        available_for_rent=data.get('available_for_rent', True)
    )
    
    db.session.add(book)
    db.session.commit()
    
    return jsonify({
        'message': 'Book added successfully',
        'book': book.to_dict()
    }), 201


@app.route('/api/books/<int:book_id>', methods=['PUT'])
@manager_required
def update_book(book_id):
    """Update book information (Manager only)"""
    book = Book.query.get(book_id)
    
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    data = request.get_json()
    
    # Update fields if provided
    if 'title' in data:
        book.title = data['title']
    if 'author' in data:
        book.author = data['author']
    if 'buy_price' in data:
        book.buy_price = float(data['buy_price'])
    if 'rent_price' in data:
        book.rent_price = float(data['rent_price'])
    if 'available_for_purchase' in data:
        book.available_for_purchase = data['available_for_purchase']
    if 'available_for_rent' in data:
        book.available_for_rent = data['available_for_rent']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Book updated successfully',
        'book': book.to_dict()
    }), 200


# ==================== Order Routes ====================

@app.route('/api/orders', methods=['POST'])
@login_required
def create_order():
    """Create a new order"""
    data = request.get_json()
    
    if not data.get('items') or len(data['items']) == 0:
        return jsonify({'error': 'Order must contain at least one item'}), 400
    
    user = User.query.get(session['user_id'])
    
    # Calculate total and create order
    total_amount = 0
    order = Order(user_id=user.id, total_amount=0)
    db.session.add(order)
    db.session.flush()  # Get order ID
    
    # Add order items
    for item_data in data['items']:
        book = Book.query.get(item_data['book_id'])
        if not book:
            db.session.rollback()
            return jsonify({'error': f'Book with ID {item_data["book_id"]} not found'}), 404
        
        transaction_type = item_data['transaction_type']
        
        if transaction_type not in ['buy', 'rent']:
            db.session.rollback()
            return jsonify({'error': 'Transaction type must be "buy" or "rent"'}), 400
        
        price = book.buy_price if transaction_type == 'buy' else book.rent_price
        total_amount += price
        
        order_item = OrderItem(
            order_id=order.id,
            book_id=book.id,
            transaction_type=transaction_type,
            price=price
        )
        db.session.add(order_item)
    
    # Update order total
    order.total_amount = total_amount
    db.session.commit()
    
    # Send email notification
    order_data = order.to_dict()
    email_service.send_bill(user.email, order_data)
    
    return jsonify({
        'message': 'Order created successfully',
        'order': order_data
    }), 201


@app.route('/api/orders', methods=['GET'])
@manager_required
def get_all_orders():
    """Get all orders (Manager only)"""
    orders = Order.query.order_by(Order.created_at.desc()).all()
    
    return jsonify({
        'orders': [order.to_dict() for order in orders]
    }), 200


@app.route('/api/orders/<int:order_id>/payment', methods=['PUT'])
@manager_required
def update_payment_status(order_id):
    """Update payment status of an order (Manager only)"""
    order = Order.query.get(order_id)
    
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    data = request.get_json()
    
    if 'payment_status' not in data:
        return jsonify({'error': 'payment_status is required'}), 400
    
    if data['payment_status'] not in ['Pending', 'Paid']:
        return jsonify({'error': 'payment_status must be "Pending" or "Paid"'}), 400
    
    order.payment_status = data['payment_status']
    db.session.commit()
    
    return jsonify({
        'message': 'Payment status updated successfully',
        'order': order.to_dict()
    }), 200


# ==================== Health Check ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok'}), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
