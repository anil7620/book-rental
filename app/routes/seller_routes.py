from flask import render_template, request, redirect, url_for, session, flash
from app import book
from .decorators import login_required
import logging
from datetime import datetime, timedelta
from bson.objectid import ObjectId 
from flask import jsonify 
from app.models.buyers import Buyer 
from app.models.sellers import Seller
from app.models.payments import Payment 
from app.models.orders import Order
from app.models.books import Book
from werkzeug.security import generate_password_hash, check_password_hash



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



@book.route('/seller_register', methods=['GET', 'POST'])
def seller_register():
    if request.method == 'POST':
        email = request.form.get("email").strip()
        password = request.form.get("password").strip()
        name = request.form.get("name").strip()
        phone = request.form.get("phone").strip()

        if Seller.exists_by_email(email):
            flash("Email already registered!", "error")
            return redirect(url_for('seller_register'))

        data = {
            "email": email,
            "name": name,
            "phone": phone,
            "password": generate_password_hash(password),
            "created_at": datetime.utcnow()
        }

        try:
            Seller.create(data)
            flash("Seller registered successfully!", "success")
            return redirect(url_for('seller_login'))
        except Exception as e:
            logger.error(f"Error during seller registration: {str(e)}")
            flash("Internal Server Error", "error")
            return redirect(url_for('seller_register'))

    return render_template('seller/register.html')


@book.route('/seller_login', methods=['GET', 'POST'])
def seller_login():
    if request.method == 'POST':
        email = request.form.get("email").strip()
        password = request.form.get("password").strip()

        if Seller.exists_by_email(email):
            seller = Seller.get_by_email(email)

            if check_password_hash(seller['password'], password):
                session["seller_id"] = str(seller['_id'])
                session["user_type"] = "seller"
                flash("Login successful", "success")
                return redirect(url_for('seller_home'))
            else:
                flash("Invalid credentials", "error")
                return redirect(url_for('seller_login'))
        else:
            flash("No such seller", "error")
            return redirect(url_for('seller_login'))

    return render_template('seller/login.html')

@book.route('/seller_home')
def seller_home():
    if session.get("user_type") != "seller":
        flash("Unauthorized access.", "error")
        return redirect(url_for('seller_login'))

    return render_template('seller/home.html')



@book.route('/seller_logout')
def seller_logout():
    session.clear()
    flash("Logged out successfully!", "success")
    return redirect(url_for('seller_login'))
