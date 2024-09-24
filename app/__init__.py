from flask import Flask
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
import os
import certifi

ca = certifi.where()

book = Flask(__name__, template_folder='templates', static_folder='static')
UPLOAD_FOLDER = os.path.join(book.root_path, 'static', 'uploads')  # Use os.path.join to get the absolute path
book.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configure MongoDB URI and JWT
book.config["MONGO_URI"] = "mongodb://localhost:27017/book_store"
book.config['JWT_SECRET_KEY'] = "adb"
book.secret_key = 'book'

# Initialize PyMongo with tlsCAFile "tlsCAFile=ca"
book.config["MONGO_OPTIONS"] = {
    "tlsCAFile": ca
}
mongo = PyMongo(book)

# Initialize JWT Manager
jwt = JWTManager(book)

# Your routes and other configurations...

if __name__ == "__main__":
    book.run(host='0.0.0.0', port=5000, debug=True)
