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
from app.models.admin import Admin
from werkzeug.security import generate_password_hash, check_password_hash



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@book.route('/admin_reg', methods=['GET'])
def admin_reg():
    try:
        # Hard-coded admin data
        email = "admin@admin.com"
        user_name = "admin"
        phone = "123-456-7890"
        password = "admin"

        # Check if the admin email is already registered
        if Admin.exists_by_email(email):
            return jsonify({"message": "Admin already registered. Check DB for details."}), 200

        # Data preparation
        data = {
            "email": email,
            "user_name": user_name,
            "phone": phone,
            "password": generate_password_hash(password)
        }

        # Create admin record
        Admin.create(data)
        return jsonify({"message": "Admin registered successfully!"}), 201

    except Exception as e:
        logger.error(f"Error during admin registration: {str(e)}")
        return "Internal Server Error", 500



@book.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get("email").strip()
        password = request.form.get("password").strip()
        
        # Check if buyer exists in the admin database
        if Admin.exists_by_email(email):
            admin = Admin.get_by_email(email)
            if check_password_hash(admin['password'], password):
                session["buyer_id"] = str(admin['_id'])
                session["buyer_type"] = "admin"
                return redirect(url_for('admin_home'))
            else:
                return "Invalid credentials", 400
        else:
            return "No such admin", 404

    return render_template('admin/login.html')


@book.route('/admin_home')
@login_required
def admin_home():
    if session["buyer_type"] == "admin":
        # Fetch count of books
        books_count = Book.count() if Book.count() else 0

        # Fetch count of buyers
        buyers_count = Buyer.count() if Buyer.count() else 0

        # Fetch count of sellers
        sellers_count = Seller.count() if Seller.count() else 0

        # Fetch count of orders
        orders_count = Order.count() if Order.count() else 0

        # Pass the counts to the template
        return render_template(
            'admin/admin_home.html',
            books_count=books_count,
            buyers_count=buyers_count,
            sellers_count=sellers_count,
            orders_count=orders_count
        )
    else:
        flash("Unauthorized access.", "error")
        return redirect(url_for('admin_login'))

 



# view all buyers

@book.route('/admin_view_buyers', methods=['GET'])
@login_required
def admin_view_buyers():
    if session["buyer_type"] != "admin":
        flash("Unauthorized access.", "error")
        return redirect(url_for('admin_home'))

    buyers = Buyer.get_all()  # Replace with the actual method call to get all buyers
    buyers = list(buyers)
    return render_template('admin/view_buyers.html', buyers=buyers)



@book.route('/admin_view_payments', methods=['GET'])
@login_required
def admin_view_payments():
    if session["buyer_type"] != "admin":
        flash("Unauthorized access.", "error")
        return redirect(url_for('admin_home'))

    payments = Payment.find_all()  # Replace with the actual method call to get all payment records
    payments = list(payments)
    return render_template('admin/view_payments.html', payments=payments)




@book.route('/view_orders')
@login_required
def view_orders():
    orders = Order.get_all()  # Assuming this method fetches all orders

    # Get book names and buyer names for each order
    for order in orders:
        product_details = []

        buyer = Buyer.get_by_id(order['buyer_id'])
        order['buyer_name'] = f"{buyer['first_name']}" if buyer else "Unknown Buyer"

    return render_template('orders/view_orders.html', orders=orders)


@book.route('/admin_view_orders', methods=['GET', 'POST'])
@login_required
def admin_view_orders():
    if session["buyer_type"] != "admin":
        flash("Unauthorized access.", "error")
        return redirect(url_for('admin_home'))
    
    if request.method == 'POST':
        order_id = request.form.get('order_id')
        new_status = request.form.get('status')
        Order.update(order_id, {"status": new_status})
        flash("Order status updated successfully.", "success")
        return redirect(url_for('admin_view_orders'))
    
    orders = Order.get_all()  # Assuming this method fetches all orders

    # Get book names and buyer names for each order
    for order in orders:
        product_details = []
        order['product_details'] = product_details
        buyer = Buyer.get_by_id(order['buyer_id'])
        order['buyer_name'] = f"{buyer['first_name']}" if buyer else "Unknown Buyer"
    return render_template('admin/view_orders.html', orders=orders)


@book.route('/view_sellers', methods=['GET'])
@login_required
def view_sellers():
    sellers = Seller.get_all()
    sellers = list(sellers)
    return render_template('admin/view_sellers.html', sellers=sellers)

@book.route('/admin_logout')
@login_required
def admin_logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('admin_login'))