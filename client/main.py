import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
from datetime import datetime


class BookstoreApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Online Bookstore")
        self.root.geometry("900x600")
        
        # API base URL
        self.api_base = "http://localhost:5000/api"
        
        # Session data
        self.session = requests.Session()
        self.current_user = None
        
        # Cart for storing selected books
        self.cart = []
        
        # Show login screen
        self.show_login_screen()
    
    def clear_window(self):
        """Clear all widgets from the window"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def show_login_screen(self):
        """Display login/registration screen"""
        self.clear_window()
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(expand=True, fill='both')
        
        # Title
        title = ttk.Label(main_frame, text="Online Bookstore", font=('Arial', 24, 'bold'))
        title.pack(pady=20)
        
        # Login Frame
        login_frame = ttk.LabelFrame(main_frame, text="Login", padding="20")
        login_frame.pack(pady=10, padx=20, fill='x')
        
        ttk.Label(login_frame, text="Username:").grid(row=0, column=0, sticky='w', pady=5)
        self.login_username = ttk.Entry(login_frame, width=30)
        self.login_username.grid(row=0, column=1, pady=5, padx=10)
        
        ttk.Label(login_frame, text="Password:").grid(row=1, column=0, sticky='w', pady=5)
        self.login_password = ttk.Entry(login_frame, show="*", width=30)
        self.login_password.grid(row=1, column=1, pady=5, padx=10)
        
        ttk.Button(login_frame, text="Login", command=self.login).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Registration Frame
        register_frame = ttk.LabelFrame(main_frame, text="Register New Account", padding="20")
        register_frame.pack(pady=10, padx=20, fill='x')
        
        ttk.Label(register_frame, text="Username:").grid(row=0, column=0, sticky='w', pady=5)
        self.reg_username = ttk.Entry(register_frame, width=30)
        self.reg_username.grid(row=0, column=1, pady=5, padx=10)
        
        ttk.Label(register_frame, text="Email:").grid(row=1, column=0, sticky='w', pady=5)
        self.reg_email = ttk.Entry(register_frame, width=30)
        self.reg_email.grid(row=1, column=1, pady=5, padx=10)
        
        ttk.Label(register_frame, text="Password:").grid(row=2, column=0, sticky='w', pady=5)
        self.reg_password = ttk.Entry(register_frame, show="*", width=30)
        self.reg_password.grid(row=2, column=1, pady=5, padx=10)
        
        ttk.Button(register_frame, text="Register", command=self.register).grid(row=3, column=0, columnspan=2, pady=10)
    
    def login(self):
        """Handle user login"""
        username = self.login_username.get()
        password = self.login_password.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password")
            return
        
        try:
            response = self.session.post(f"{self.api_base}/login", json={
                'username': username,
                'password': password
            })
            
            if response.status_code == 200:
                data = response.json()
                self.current_user = data['user']
                messagebox.showinfo("Success", "Login successful!")
                
                # Show appropriate interface based on user role
                if self.current_user['is_manager']:
                    self.show_manager_interface()
                else:
                    self.show_customer_interface()
            else:
                messagebox.showerror("Error", response.json().get('error', 'Login failed'))
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")
    
    def register(self):
        """Handle user registration"""
        username = self.reg_username.get()
        email = self.reg_email.get()
        password = self.reg_password.get()
        
        if not username or not email or not password:
            messagebox.showerror("Error", "All fields are required")
            return
        
        try:
            response = self.session.post(f"{self.api_base}/register", json={
                'username': username,
                'email': email,
                'password': password
            })
            
            if response.status_code == 201:
                messagebox.showinfo("Success", "Registration successful! Please login.")
                self.reg_username.delete(0, tk.END)
                self.reg_email.delete(0, tk.END)
                self.reg_password.delete(0, tk.END)
            else:
                messagebox.showerror("Error", response.json().get('error', 'Registration failed'))
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")
    
    def show_customer_interface(self):
        """Display customer interface"""
        self.clear_window()
        
        # Top bar
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(top_frame, text=f"Welcome, {self.current_user['username']}!", 
                 font=('Arial', 12, 'bold')).pack(side='left')
        ttk.Button(top_frame, text="Logout", command=self.logout).pack(side='right')
        ttk.Button(top_frame, text=f"View Cart ({len(self.cart)})", 
                  command=self.show_cart).pack(side='right', padx=5)
        
        # Search frame
        search_frame = ttk.Frame(self.root)
        search_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(search_frame, text="Search Books:").pack(side='left', padx=5)
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.pack(side='left', padx=5)
        ttk.Button(search_frame, text="Search", command=self.search_books).pack(side='left', padx=5)
        ttk.Button(search_frame, text="Show All", command=lambda: self.search_books('')).pack(side='left')
        
        # Results frame
        results_frame = ttk.Frame(self.root)
        results_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Treeview for books
        columns = ('ID', 'Title', 'Author', 'Buy Price', 'Rent Price')
        self.books_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.books_tree.heading(col, text=col)
            if col == 'ID':
                self.books_tree.column(col, width=50)
            elif col in ['Buy Price', 'Rent Price']:
                self.books_tree.column(col, width=100)
            else:
                self.books_tree.column(col, width=200)
        
        self.books_tree.pack(side='left', fill='both', expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient='vertical', command=self.books_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.books_tree.configure(yscrollcommand=scrollbar.set)
        
        # Action buttons
        action_frame = ttk.Frame(self.root)
        action_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(action_frame, text="Add to Cart (Buy)", 
                  command=lambda: self.add_to_cart('buy')).pack(side='left', padx=5)
        ttk.Button(action_frame, text="Add to Cart (Rent)", 
                  command=lambda: self.add_to_cart('rent')).pack(side='left', padx=5)
        
        # Load all books initially
        self.search_books('')
    
    def search_books(self, keyword=None):
        """Search for books"""
        if keyword is None:
            keyword = self.search_entry.get()
        
        try:
            response = self.session.get(f"{self.api_base}/books/search", params={'keyword': keyword})
            
            if response.status_code == 200:
                books = response.json()['books']
                
                # Clear existing items
                for item in self.books_tree.get_children():
                    self.books_tree.delete(item)
                
                # Add books to treeview
                for book in books:
                    self.books_tree.insert('', 'end', values=(
                        book['id'],
                        book['title'],
                        book['author'],
                        f"${book['buy_price']:.2f}",
                        f"${book['rent_price']:.2f}"
                    ))
            else:
                messagebox.showerror("Error", "Failed to fetch books")
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")
    
    def add_to_cart(self, transaction_type):
        """Add selected book to cart"""
        selection = self.books_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a book")
            return
        
        for item in selection:
            values = self.books_tree.item(item)['values']
            book_id = values[0]
            title = values[1]
            author = values[2]
            
            # Check if already in cart
            for cart_item in self.cart:
                if cart_item['book_id'] == book_id and cart_item['transaction_type'] == transaction_type:
                    messagebox.showinfo("Info", f"{title} ({transaction_type}) is already in cart")
                    return
            
            self.cart.append({
                'book_id': book_id,
                'title': title,
                'author': author,
                'transaction_type': transaction_type
            })
        
        messagebox.showinfo("Success", f"Added to cart ({transaction_type})")
        # Update cart button text
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Button) and "View Cart" in child['text']:
                        child.config(text=f"View Cart ({len(self.cart)})")
    
    def show_cart(self):
        """Display shopping cart"""
        if not self.cart:
            messagebox.showinfo("Cart", "Your cart is empty")
            return
        
        # Create cart window
        cart_window = tk.Toplevel(self.root)
        cart_window.title("Shopping Cart")
        cart_window.geometry("600x400")
        
        # Cart items
        frame = ttk.Frame(cart_window)
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Treeview
        columns = ('Title', 'Author', 'Type')
        cart_tree = ttk.Treeview(frame, columns=columns, show='headings')
        
        for col in columns:
            cart_tree.heading(col, text=col)
            cart_tree.column(col, width=150)
        
        for item in self.cart:
            cart_tree.insert('', 'end', values=(
                item['title'],
                item['author'],
                item['transaction_type'].upper()
            ))
        
        cart_tree.pack(fill='both', expand=True)
        
        # Buttons
        button_frame = ttk.Frame(cart_window)
        button_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(button_frame, text="Remove Selected", 
                  command=lambda: self.remove_from_cart(cart_tree, cart_window)).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Place Order", 
                  command=lambda: self.place_order(cart_window)).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Clear Cart", 
                  command=lambda: self.clear_cart(cart_window)).pack(side='right', padx=5)
    
    def remove_from_cart(self, tree, window):
        """Remove selected item from cart"""
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to remove")
            return
        
        item = tree.item(selection[0])
        values = item['values']
        
        # Find and remove from cart
        for i, cart_item in enumerate(self.cart):
            if cart_item['title'] == values[0] and cart_item['transaction_type'] == values[2].lower():
                self.cart.pop(i)
                break
        
        tree.delete(selection[0])
        messagebox.showinfo("Success", "Item removed from cart")
    
    def clear_cart(self, window):
        """Clear all items from cart"""
        if messagebox.askyesno("Confirm", "Clear all items from cart?"):
            self.cart = []
            window.destroy()
            messagebox.showinfo("Success", "Cart cleared")
    
    def place_order(self, window):
        """Place order with items in cart"""
        if not self.cart:
            messagebox.showwarning("Warning", "Cart is empty")
            return
        
        if not messagebox.askyesno("Confirm", "Place this order?"):
            return
        
        try:
            # Prepare order data
            items = [{'book_id': item['book_id'], 'transaction_type': item['transaction_type']} 
                    for item in self.cart]
            
            response = self.session.post(f"{self.api_base}/orders", json={'items': items})
            
            if response.status_code == 201:
                order_data = response.json()['order']
                messagebox.showinfo("Success", 
                    f"Order placed successfully!\nOrder ID: {order_data['id']}\n"
                    f"Total: ${order_data['total_amount']:.2f}\n"
                    f"A bill has been sent to your email.")
                self.cart = []
                window.destroy()
            else:
                messagebox.showerror("Error", response.json().get('error', 'Order failed'))
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")
    
    def show_manager_interface(self):
        """Display manager interface"""
        self.clear_window()
        
        # Top bar
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(top_frame, text=f"Manager Dashboard - {self.current_user['username']}", 
                 font=('Arial', 12, 'bold')).pack(side='left')
        ttk.Button(top_frame, text="Logout", command=self.logout).pack(side='right')
        
        # Notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Orders tab
        orders_tab = ttk.Frame(notebook)
        notebook.add(orders_tab, text="Manage Orders")
        self.create_orders_tab(orders_tab)
        
        # Books tab
        books_tab = ttk.Frame(notebook)
        notebook.add(books_tab, text="Manage Books")
        self.create_books_tab(books_tab)
    
    def create_orders_tab(self, parent):
        """Create orders management tab"""
        # Refresh button
        ttk.Button(parent, text="Refresh Orders", command=lambda: self.load_orders()).pack(pady=5)
        
        # Treeview for orders
        columns = ('Order ID', 'User Email', 'Total', 'Status', 'Date')
        self.orders_tree = ttk.Treeview(parent, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.orders_tree.heading(col, text=col)
            if col == 'Order ID':
                self.orders_tree.column(col, width=80)
            elif col in ['Total']:
                self.orders_tree.column(col, width=100)
            else:
                self.orders_tree.column(col, width=150)
        
        self.orders_tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(parent, orient='vertical', command=self.orders_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.orders_tree.configure(yscrollcommand=scrollbar.set)
        
        # Action buttons
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(action_frame, text="View Order Details", 
                  command=self.view_order_details).pack(side='left', padx=5)
        ttk.Button(action_frame, text="Mark as Paid", 
                  command=lambda: self.update_payment_status('Paid')).pack(side='left', padx=5)
        ttk.Button(action_frame, text="Mark as Pending", 
                  command=lambda: self.update_payment_status('Pending')).pack(side='left', padx=5)
        
        # Load orders
        self.load_orders()
    
    def load_orders(self):
        """Load all orders"""
        try:
            response = self.session.get(f"{self.api_base}/orders")
            
            if response.status_code == 200:
                orders = response.json()['orders']
                
                # Clear existing items
                for item in self.orders_tree.get_children():
                    self.orders_tree.delete(item)
                
                # Add orders to treeview
                for order in orders:
                    self.orders_tree.insert('', 'end', values=(
                        order['id'],
                        order['user_email'],
                        f"${order['total_amount']:.2f}",
                        order['payment_status'],
                        order['created_at'][:19]
                    ), tags=(str(order['id']),))
            else:
                messagebox.showerror("Error", "Failed to fetch orders")
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")
    
    def view_order_details(self):
        """View detailed order information"""
        selection = self.orders_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an order")
            return
        
        order_id = self.orders_tree.item(selection[0])['values'][0]
        
        try:
            response = self.session.get(f"{self.api_base}/orders")
            if response.status_code == 200:
                orders = response.json()['orders']
                order = next((o for o in orders if o['id'] == order_id), None)
                
                if order:
                    # Create details window
                    details_window = tk.Toplevel(self.root)
                    details_window.title(f"Order #{order_id} Details")
                    details_window.geometry("500x400")
                    
                    # Order info
                    info_frame = ttk.Frame(details_window, padding="10")
                    info_frame.pack(fill='x')
                    
                    ttk.Label(info_frame, text=f"Order ID: {order['id']}", 
                             font=('Arial', 12, 'bold')).pack(anchor='w')
                    ttk.Label(info_frame, text=f"Customer Email: {order['user_email']}").pack(anchor='w')
                    ttk.Label(info_frame, text=f"Date: {order['created_at'][:19]}").pack(anchor='w')
                    ttk.Label(info_frame, text=f"Status: {order['payment_status']}").pack(anchor='w')
                    ttk.Label(info_frame, text=f"Total: ${order['total_amount']:.2f}", 
                             font=('Arial', 11, 'bold')).pack(anchor='w')
                    
                    # Items
                    ttk.Label(details_window, text="Order Items:", 
                             font=('Arial', 11, 'bold')).pack(anchor='w', padx=10, pady=5)
                    
                    items_frame = ttk.Frame(details_window)
                    items_frame.pack(fill='both', expand=True, padx=10, pady=5)
                    
                    columns = ('Book', 'Author', 'Type', 'Price')
                    items_tree = ttk.Treeview(items_frame, columns=columns, show='headings')
                    
                    for col in columns:
                        items_tree.heading(col, text=col)
                    
                    for item in order['items']:
                        items_tree.insert('', 'end', values=(
                            item['book_title'],
                            item['book_author'],
                            item['transaction_type'].upper(),
                            f"${item['price']:.2f}"
                        ))
                    
                    items_tree.pack(fill='both', expand=True)
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")
    
    def update_payment_status(self, status):
        """Update payment status of selected order"""
        selection = self.orders_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an order")
            return
        
        order_id = self.orders_tree.item(selection[0])['values'][0]
        
        try:
            response = self.session.put(f"{self.api_base}/orders/{order_id}/payment", 
                                       json={'payment_status': status})
            
            if response.status_code == 200:
                messagebox.showinfo("Success", f"Payment status updated to {status}")
                self.load_orders()
            else:
                messagebox.showerror("Error", response.json().get('error', 'Update failed'))
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")
    
    def create_books_tab(self, parent):
        """Create books management tab"""
        # Top buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x', pady=5)
        
        ttk.Button(button_frame, text="Refresh Books", 
                  command=lambda: self.load_manager_books()).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Add New Book", 
                  command=self.add_book_dialog).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Edit Selected", 
                  command=self.edit_book_dialog).pack(side='left', padx=5)
        
        # Treeview for books
        columns = ('ID', 'Title', 'Author', 'Buy Price', 'Rent Price', 'Available Buy', 'Available Rent')
        self.manager_books_tree = ttk.Treeview(parent, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.manager_books_tree.heading(col, text=col)
            if col == 'ID':
                self.manager_books_tree.column(col, width=50)
            elif col in ['Buy Price', 'Rent Price']:
                self.manager_books_tree.column(col, width=80)
            elif col in ['Available Buy', 'Available Rent']:
                self.manager_books_tree.column(col, width=100)
            else:
                self.manager_books_tree.column(col, width=150)
        
        self.manager_books_tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Load books
        self.load_manager_books()
    
    def load_manager_books(self):
        """Load all books for manager"""
        try:
            response = self.session.get(f"{self.api_base}/books/search", params={'keyword': ''})
            
            if response.status_code == 200:
                books = response.json()['books']
                
                # Clear existing items
                for item in self.manager_books_tree.get_children():
                    self.manager_books_tree.delete(item)
                
                # Add books to treeview
                for book in books:
                    self.manager_books_tree.insert('', 'end', values=(
                        book['id'],
                        book['title'],
                        book['author'],
                        f"${book['buy_price']:.2f}",
                        f"${book['rent_price']:.2f}",
                        'Yes' if book['available_for_purchase'] else 'No',
                        'Yes' if book['available_for_rent'] else 'No'
                    ))
            else:
                messagebox.showerror("Error", "Failed to fetch books")
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")
    
    def add_book_dialog(self):
        """Show dialog to add new book"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Book")
        dialog.geometry("400x300")
        
        # Form fields
        ttk.Label(dialog, text="Title:").grid(row=0, column=0, padx=10, pady=5, sticky='w')
        title_entry = ttk.Entry(dialog, width=30)
        title_entry.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Author:").grid(row=1, column=0, padx=10, pady=5, sticky='w')
        author_entry = ttk.Entry(dialog, width=30)
        author_entry.grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Buy Price:").grid(row=2, column=0, padx=10, pady=5, sticky='w')
        buy_price_entry = ttk.Entry(dialog, width=30)
        buy_price_entry.grid(row=2, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Rent Price:").grid(row=3, column=0, padx=10, pady=5, sticky='w')
        rent_price_entry = ttk.Entry(dialog, width=30)
        rent_price_entry.grid(row=3, column=1, padx=10, pady=5)
        
        def submit():
            title = title_entry.get()
            author = author_entry.get()
            buy_price = buy_price_entry.get()
            rent_price = rent_price_entry.get()
            
            if not all([title, author, buy_price, rent_price]):
                messagebox.showerror("Error", "All fields are required")
                return
            
            try:
                response = self.session.post(f"{self.api_base}/books", json={
                    'title': title,
                    'author': author,
                    'buy_price': float(buy_price),
                    'rent_price': float(rent_price)
                })
                
                if response.status_code == 201:
                    messagebox.showinfo("Success", "Book added successfully")
                    dialog.destroy()
                    self.load_manager_books()
                else:
                    messagebox.showerror("Error", response.json().get('error', 'Failed to add book'))
            except ValueError:
                messagebox.showerror("Error", "Invalid price format")
            except Exception as e:
                messagebox.showerror("Error", f"Connection error: {str(e)}")
        
        ttk.Button(dialog, text="Add Book", command=submit).grid(row=4, column=0, columnspan=2, pady=20)
    
    def edit_book_dialog(self):
        """Show dialog to edit selected book"""
        selection = self.manager_books_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a book to edit")
            return
        
        values = self.manager_books_tree.item(selection[0])['values']
        book_id = values[0]
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit Book #{book_id}")
        dialog.geometry("400x350")
        
        # Form fields with current values
        ttk.Label(dialog, text="Title:").grid(row=0, column=0, padx=10, pady=5, sticky='w')
        title_entry = ttk.Entry(dialog, width=30)
        title_entry.insert(0, values[1])
        title_entry.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Author:").grid(row=1, column=0, padx=10, pady=5, sticky='w')
        author_entry = ttk.Entry(dialog, width=30)
        author_entry.insert(0, values[2])
        author_entry.grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Buy Price:").grid(row=2, column=0, padx=10, pady=5, sticky='w')
        buy_price_entry = ttk.Entry(dialog, width=30)
        buy_price_entry.insert(0, values[3].replace('$', ''))
        buy_price_entry.grid(row=2, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Rent Price:").grid(row=3, column=0, padx=10, pady=5, sticky='w')
        rent_price_entry = ttk.Entry(dialog, width=30)
        rent_price_entry.insert(0, values[4].replace('$', ''))
        rent_price_entry.grid(row=3, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Available for Purchase:").grid(row=4, column=0, padx=10, pady=5, sticky='w')
        available_buy = tk.BooleanVar(value=values[5] == 'Yes')
        ttk.Checkbutton(dialog, variable=available_buy).grid(row=4, column=1, padx=10, pady=5, sticky='w')
        
        ttk.Label(dialog, text="Available for Rent:").grid(row=5, column=0, padx=10, pady=5, sticky='w')
        available_rent = tk.BooleanVar(value=values[6] == 'Yes')
        ttk.Checkbutton(dialog, variable=available_rent).grid(row=5, column=1, padx=10, pady=5, sticky='w')
        
        def submit():
            title = title_entry.get()
            author = author_entry.get()
            buy_price = buy_price_entry.get()
            rent_price = rent_price_entry.get()
            
            if not all([title, author, buy_price, rent_price]):
                messagebox.showerror("Error", "All fields are required")
                return
            
            try:
                response = self.session.put(f"{self.api_base}/books/{book_id}", json={
                    'title': title,
                    'author': author,
                    'buy_price': float(buy_price),
                    'rent_price': float(rent_price),
                    'available_for_purchase': available_buy.get(),
                    'available_for_rent': available_rent.get()
                })
                
                if response.status_code == 200:
                    messagebox.showinfo("Success", "Book updated successfully")
                    dialog.destroy()
                    self.load_manager_books()
                else:
                    messagebox.showerror("Error", response.json().get('error', 'Failed to update book'))
            except ValueError:
                messagebox.showerror("Error", "Invalid price format")
            except Exception as e:
                messagebox.showerror("Error", f"Connection error: {str(e)}")
        
        ttk.Button(dialog, text="Update Book", command=submit).grid(row=6, column=0, columnspan=2, pady=20)
    
    def logout(self):
        """Logout current user"""
        try:
            self.session.post(f"{self.api_base}/logout")
        except:
            pass
        
        self.current_user = None
        self.cart = []
        self.show_login_screen()


def main():
    root = tk.Tk()
    app = BookstoreApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
