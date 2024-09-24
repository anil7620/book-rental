from app import book
from app.routes import  admin_routes, order_routes
from app.routes import payment_routes, auth_routes, book_routes, seller_routes, buyer_routes, admin_routes
if __name__ == "__main__":
     book.run(host='0.0.0.0', port=5001, debug=True)

