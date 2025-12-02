import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()


class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_username = os.getenv('SMTP_USERNAME', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.sender_email = os.getenv('SENDER_EMAIL', self.smtp_username)
    
    def send_bill(self, recipient_email, order_data):
        """
        Send order bill to customer email
        
        Args:
            recipient_email: Customer's email address
            order_data: Dictionary containing order details
        """
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = f"Order Confirmation - Order #{order_data['id']}"
            message["From"] = self.sender_email
            message["To"] = recipient_email
            
            # Create HTML content
            html_content = self._generate_bill_html(order_data)
            
            # Create plain text version
            text_content = self._generate_bill_text(order_data)
            
            # Attach parts
            part1 = MIMEText(text_content, "plain")
            part2 = MIMEText(html_content, "html")
            message.attach(part1)
            message.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.sendmail(self.sender_email, recipient_email, message.as_string())
            
            print(f"Bill sent successfully to {recipient_email}")
            return True
            
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
    
    def _generate_bill_text(self, order_data):
        """Generate plain text bill"""
        text = f"""
BOOKSTORE ORDER CONFIRMATION
=============================

Order ID: {order_data['id']}
Date: {order_data['created_at']}
Payment Status: {order_data['payment_status']}

ORDER DETAILS:
--------------
"""
        for item in order_data['items']:
            text += f"\n{item['book_title']} by {item['book_author']}\n"
            text += f"  Type: {item['transaction_type'].upper()}\n"
            text += f"  Price: ${item['price']:.2f}\n"
        
        text += f"\n--------------\nTOTAL: ${order_data['total_amount']:.2f}\n"
        text += "\nThank you for your order!\n"
        
        return text
    
    def _generate_bill_html(self, order_data):
        """Generate HTML bill"""
        items_html = ""
        for item in order_data['items']:
            items_html += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #ddd;">{item['book_title']}</td>
                <td style="padding: 10px; border-bottom: 1px solid #ddd;">{item['book_author']}</td>
                <td style="padding: 10px; border-bottom: 1px solid #ddd;">{item['transaction_type'].upper()}</td>
                <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right;">${item['price']:.2f}</td>
            </tr>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; background-color: white; }}
                th {{ background-color: #4CAF50; color: white; padding: 12px; text-align: left; }}
                .total {{ font-size: 1.2em; font-weight: bold; text-align: right; padding: 20px; background-color: #fff; }}
                .footer {{ text-align: center; padding: 20px; color: #777; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Order Confirmation</h1>
                </div>
                <div class="content">
                    <p><strong>Order ID:</strong> #{order_data['id']}</p>
                    <p><strong>Date:</strong> {order_data['created_at']}</p>
                    <p><strong>Payment Status:</strong> {order_data['payment_status']}</p>
                    
                    <h2>Order Details</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Book Title</th>
                                <th>Author</th>
                                <th>Type</th>
                                <th>Price</th>
                            </tr>
                        </thead>
                        <tbody>
                            {items_html}
                        </tbody>
                    </table>
                    
                    <div class="total">
                        TOTAL: ${order_data['total_amount']:.2f}
                    </div>
                </div>
                <div class="footer">
                    <p>Thank you for shopping with us!</p>
                    <p>For any questions, please contact our support team.</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html
