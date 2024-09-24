from flask import render_template, request, redirect, url_for, session
from app import book
from app.models.buyers import Buyer
from app.models.books import Book 

from app.models.admin import Admin
from werkzeug.security import generate_password_hash, check_password_hash 
import logging
from bson import ObjectId
from .decorators import login_required
from flask import send_from_directory

from flask import flash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@book.route('/')
def index():
    books = Book.get_all()
    return render_template('index.html', books=books)


@book.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(book.config['UPLOAD_FOLDER'], filename)

import random
@book.route('/buyer_home')
@login_required
def buyer_home():
    if session.get("buyer_type") != "buyer":
        flash("Unauthorized access.", "error")
        return redirect(url_for('buyer_login'))
    
    books = Book.get_all()   
    return render_template('index.html', session=session, books=books)


@book.route('/buyer_login', methods=['GET', 'POST'])
def buyer_login():
    if request.method == 'POST':
        email = request.form.get("email").strip()
        password = request.form.get("password").strip()
        
        if Buyer.exists_by_email(email):
            buyer = Buyer.get_by_email(email)
            if check_password_hash(buyer['password'], password):
                session["buyer_id"] = str(buyer['_id'])
                session["buyer_type"] = "buyer"
                next_page = session.get('next', url_for('buyer_home'))
                session.pop('next', None) 
                return redirect(next_page)
            else:
                flash('Invalid credentials', 'error')
        else:
            flash('No such buyer', 'error')

    next_page = request.args.get('next')
    if next_page:
        session['next'] = next_page  

    return render_template('buyer/login.html')





@book.route('/register_buyer', methods=['GET', 'POST'])
def register_buyer(): 
    try:
        if request.method == 'POST':
            email = request.form.get("email").strip()
            password = request.form.get("password").strip()
            confirm_password = request.form.get("confirm_password").strip()

            if Buyer.exists_by_email(email):
                return "Email already registered", 400

            if password != confirm_password:
                return "Passwords do not match", 400

            data = {
                "name": request.form.get("name").strip(),
                "email": email,
                "phone": request.form.get("phone").strip(),  
                "password": generate_password_hash(password)
            }

            Buyer.create(data)
            return redirect(url_for('buyer_login'))

        return render_template('buyer/register.html')
    except Exception as e:
        logger.error(f"Error during buyer registration: {str(e)}")
        return "Internal Server Error", 500
 
@book.route('/logout')
def logout():
    try:
        session.clear()  
        session.pop('buyer_id', None)
        session.pop('buyer_type', None)
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        return "Internal Server Error", 500



 