from flask import render_template, request, redirect, url_for, session, jsonify, flash
from app import book
from app.models.buyers import Buyer
from app.models.admin import Admin 
from app.models.books import Book
from app.models.orders import Order
from .decorators import login_required
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import json
from functools import wraps







@book.route('/get_all_products')
def get_all_products():
    books = Book.get_all()
    
    
    product_ids = [str(book['_id']) for book in books]


    return render_template('index.html', books=books)






@book.route('/view_buyers')
@login_required
def view_buyers():
    buyers = Buyer.get_all()
    return render_template('buyers/view_buyers.html', buyers=buyers)

@book.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        # Fetch form data
        title = request.form.get('title').strip()
        author = request.form.get('author').strip()
        genre = request.form.get('genre').strip()
        condition = request.form.get('condition').strip()  # Example: new, good, fair, bad
        weekly_price = request.form.get('weekly_price').strip()
        monthly_price = request.form.get('monthly_price').strip()
        availability = request.form.get('availability').strip()  # Example: Available, Unavailable
        description = request.form.get('description').strip()
        status = request.form.get('status').strip()  # Example: Active, Inactive
        image_url = request.form.get('image_url').strip()  # Book image URL
        seller_id = session.get('seller_id')  # Assuming seller_id is stored in session

        # Create the book data dictionary
        data = {
            'title': title,
            'author': author,
            'genre': genre,
            'condition': condition,
            'weekly_price': weekly_price,
            'monthly_price': monthly_price,
            'availability': availability,
            'description': description,
            'status': status,
            'image_url': image_url,  # Include the image URL
            'seller_id': seller_id,
            'created_at': datetime.now()  # Set the created_at timestamp
        }

        # Save the book to the database
        try:
            Book.create(data)
            flash('Book added successfully!', 'success')
            return redirect(url_for('view_books'))  # Redirect to a page where books can be viewed
        except Exception as e:
            flash(f"Error adding book: {e}", 'error')
            return redirect(url_for('add_book'))

    return render_template('books/add_book.html')


@book.route('/edit_book/<book_id>', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    book = Book.get_by_id(book_id)

    if request.method == 'POST':
        title = request.form.get('title').strip()
        author = request.form.get('author').strip()
        genre = request.form.get('genre').strip()
        condition = request.form.get('condition').strip()  # Example: bad, good, new, fair
        weekly_price = request.form.get('weekly_price').strip()
        monthly_price = request.form.get('monthly_price').strip()
        availability = request.form.get('availability').strip()  # Example: Available, Unavailable
        description = request.form.get('description').strip()
        status = request.form.get('status').strip()  # Example: Active, Inactive

        # Create the book data dictionary
        data = {
            'title': title,
            'author': author,
            'genre': genre,
            'condition': condition,
            'weekly_price': weekly_price,
            'monthly_price': monthly_price,
            'availability': availability,
            'description': description,
            'status': status
        }

        # Save the book to the database
        try:
            Book.update(book_id, data)
            flash('Book updated successfully!', 'success')
            return redirect(url_for('view_books'))
        except Exception as e:
            flash(f"Error updating book: {e}", 'error')
            return redirect(url_for('edit_book', book_id=book_id))

    return render_template('books/edit_book.html', book=book)


@book.route('/delete_book/<book_id>')
@login_required
def delete_book(book_id):
    try:
        Book.delete(book_id)
        flash('Book deleted successfully!', 'success')
    except Exception as e:
        flash(f"Error deleting book: {e}", 'error')

    return redirect(url_for('view_books'))


@book.route('/admin_view_books')
def admin_view_books():
    books = Book.get_all()
    return render_template('books/admin_view_books.html', books=books)



@book.route('/view_books')
def view_books():
    books = Book.get_all()
    return render_template('books/view_books.html', books=books)

@book.route('/view_book/<book_id>', methods=['GET'])
def view_book(book_id):
    book = Book.get_by_id(book_id)
    if not book:
        flash('Book not found', 'error')
        return redirect(url_for('view_books'))
    
    return render_template('books/view_book.html', book=book)


@book.route('/view_rental_history')
@login_required
def view_rental_history():
    orders = Order.get_all()
    return render_template('orders/view_rental_history.html', orders=orders)