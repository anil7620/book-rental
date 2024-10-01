from flask import render_template, request, redirect, url_for, session, jsonify, flash
from app import book
from app.models.buyers import Buyer
from app.models.admin import Admin
from app.models.books import Book
from bson import ObjectId
from .decorators import login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app.models.orders import Order
from datetime import datetime
import json
from functools import wraps
import logging

import os 


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@book.route('/rent_book/<book_id>', methods=['GET', 'POST'])
def rent_book(book_id):
    user_id = session.get('buyer_id')
    
    # Assuming Book.get_by_id returns a dictionary, access it as a dictionary
    book = Book.get_by_id(book_id)
    user = Buyer.get_by_id(user_id)

    if not book:
        flash('Book not found', 'error')
        return redirect(url_for('index'))
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('buyer_login'))

    if request.method == 'POST':
        rent_type = request.form.get('rent_type')
        
        # Access as dictionary keys instead of attributes
        price = book['weekly_price'] if rent_type == 'weekly' else book['monthly_price']

        # Create a pending order and redirect to checkout
        order_data = {
            'book_id': book_id,
            'buyer_id': user_id,
            'status': 'pending',
            'duration': rent_type,
            'price': price,
            'created_at': datetime.now(),
        }
        order = Order.create(order_data)

        return redirect(url_for('checkout', order_id=order.inserted_id))

    return render_template('books/rent_book.html', book=book)




@book.route('/view_buyer_orders')
@login_required
def view_buyer_orders():
    user_id = session.get('buyer_id')

    # Get all orders for the buyer
    orders = Order.get_by_buyer_id(user_id)

    # Fetch the book details for each order
    for order in orders:
        book = Book.get_by_id(order['book_id'])  # Assuming Book.get_by_id returns a book as a dictionary
        order['book'] = book  # Attach the book details to the order

    return render_template('orders/view_buyer_orders.html', orders=orders)
