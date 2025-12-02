# Online Bookstore Application

A desktop application for an online bookstore with a Flask REST API backend and Tkinter GUI frontend.

## Features

### Customer Features
- User registration and login
- Search books by title or author
- Buy and rent books
- Receive email bills for orders

### Manager Features
- Secure manager login
- View all orders (buy and rental)
- Update payment status
- Add and update book information

## Technology Stack

- **Backend**: Python Flask REST API
- **Database**: MySQL
- **Frontend**: Python Tkinter (Desktop GUI)
- **Authentication**: Session-based with secure password hashing (bcrypt)
- **Email**: SMTP integration for bill notifications

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- MySQL Server
- pip (Python package manager)

### Installation

1. **Clone or navigate to the project directory**

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up MySQL Database**
   - Start your MySQL server
   - Create a database named `bookstore`:
     ```sql
     CREATE DATABASE bookstore;
     ```

4. **Configure Environment Variables**
   - Copy `.env.example` to `.env`
   - Update the values in `.env` with your configuration:
     - Database credentials
     - SMTP email settings (for Gmail, use an App Password)
     - Flask secret key

5. **Initialize the Database**
   ```bash
   python backend/init_db.py
   ```

6. **Run the Flask Backend**
   ```bash
   python backend/app.py
   ```
   The API will be available at `http://localhost:5000`

7. **Run the Desktop Client**
   Open a new terminal and run:
   ```bash
   python client/main.py
   ```

## Default Manager Account

After initializing the database, a default manager account is created:
- **Username**: `admin`
- **Password**: `admin123`

**Important**: Change this password after first login!

## Project Structure

```
finalproject/
├── backend/
│   ├── app.py              # Flask application and API endpoints
│   ├── models.py           # Database models
│   ├── init_db.py          # Database initialization script
│   └── email_service.py    # Email notification service
├── client/
│   └── main.py             # Tkinter desktop GUI application
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
└── README.md              # This file
```

## API Endpoints

### Authentication
- `POST /api/register` - Register new customer
- `POST /api/login` - User/Manager login
- `POST /api/logout` - Logout

### Books
- `GET /api/books/search?keyword=<query>` - Search books

### Orders
- `POST /api/orders` - Create new order
- `GET /api/orders` - Get all orders (Manager only)
- `PUT /api/orders/<order_id>/payment` - Update payment status (Manager only)

### Manager
- `POST /api/books` - Add new book (Manager only)
- `PUT /api/books/<book_id>` - Update book (Manager only)

## Usage

### Customer Flow
1. Register a new account or login
2. Search for books by title or author
3. Select books to buy or rent
4. Place order
5. Receive bill via email

### Manager Flow
1. Login with manager credentials
2. View all orders
3. Update payment status for orders
4. Add or update book information

## Security Features
- Passwords hashed with bcrypt
- Session-based authentication
- Role-based access control (Customer vs Manager)
- Protected API endpoints

## Email Configuration

For Gmail:
1. Enable 2-factor authentication
2. Generate an App Password
3. Use the App Password in `.env` file

## Troubleshooting

- **Database connection error**: Verify MySQL is running and credentials in `.env` are correct
- **Email sending fails**: Check SMTP settings and use App Password for Gmail
- **API connection error**: Ensure Flask backend is running on port 5000

## Future Enhancements
- User order history
- Book reviews and ratings
- Inventory management
- Advanced search filters
- Book return system for rentals
