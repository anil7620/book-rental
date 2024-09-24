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

    book = Book.get_by_id(book_id)
    user = Buyer.get_by_id(user_id)

    if not book:
        flash('Book not found', 'error')
        return redirect(url_for('index'))  
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('buyer_login')) 

    if request.method == 'POST':
        order_data = {
            'book_id': book_id,
            'buyer_id': user_id,
            'status': 'pending',
            'created_at': datetime.now(),
        }
        try:
            Order.create(order_data)
            flash('Book rented successfully', 'success')
        except Exception as e:
            flash(f'Error renting book: {str(e)}', 'error')

        return redirect(url_for('view_book', book_id=book_id))

    return render_template('books/rent_book.html', book=book)



@book.route('/view_buyer_orders')
@login_required
def view_buyer_orders():
    user_id = session.get('buyer_id')

    orders = Order.get_by_buyer_id(user_id)

    return render_template('orders/view_buyer_orders.html', orders=orders)