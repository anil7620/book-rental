from flask import render_template, request, redirect, url_for, session, flash
from app import book
from app.models.buyers import Buyer
from app.models.admin import Admin
from app.models.orders import Order
from app.models.books import Book
from app.models.payments import Payment
from .decorators import login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from bson import ObjectId

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@book.route('/checkout/<order_id>', methods=['GET', 'POST'])
def checkout(order_id):
    user_id = session.get('buyer_id')

    # Convert order_id to ObjectId for MongoDB query
    order = Order.get_order_by_id(ObjectId(order_id))
    book = Book.get_by_id(order['book_id'])  # Assuming book_id is in the order document

    if not order or not book:
        flash('Invalid order or book', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Get form data
        card_name = request.form.get('card_name')
        card_number = request.form.get('card_number')
        expiry_date = request.form.get('expiry_date')
        cvv = request.form.get('cvv')

        # Basic validation (you can expand this further)
        if not (card_name and card_number and expiry_date and cvv):
            flash('All fields are required', 'error')
            return redirect(url_for('checkout', order_id=order_id))

        # Simulate payment processing
        try:
            # In a real app, you'd integrate with a payment processor here
            payment_data = {
                'order_id': order['_id'],
                'buyer_id': user_id,
                'amount': order['price'],
                'status': 'completed',
                'created_at': datetime.now(),
                'payment_method': 'credit_card',
                'card_name': card_name,
                'card_number': card_number,  # Be cautious, never store raw card numbers in production
                'expiry_date': expiry_date,
                'cvv': cvv  # Never store CVV in production, this is just for demonstration
            }

            # Save payment details to the database
            Payment.create(payment_data)
            
            # Update order status to 'completed'
            Order.update(order['_id'], {'status': 'completed'})

            flash('Payment successful! Book rented.', 'success')
            return redirect(url_for('view_buyer_orders'))

        except Exception as e:
            logger.error(f"Payment error: {str(e)}")
            flash('Payment failed. Please try again.', 'error')

    return render_template('payment/checkout.html', order=order, book=book)
