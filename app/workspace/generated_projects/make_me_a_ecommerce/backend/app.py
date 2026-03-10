from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid

app = Flask(__name__)
CORS(app)

products = []
categories = []
orders = []
users = []
reviews = []
carts = []
payment_methods = []

@app.route('/')
def root():
    return jsonify({"message": "API is running", "endpoints": [
        "/api/health",
        "/api/products",
        "/api/products/:id",
        "/api/cart",
        "/api/cart/:id",
        "/api/orders",
        "/api/orders/:id",
        "/api/users",
        "/api/users/:id",
        "/api/reviews",
        "/api/reviews/:id"
    ]})

@app.route('/api/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/api/products', methods=['GET'])
def get_products():
    return jsonify(products)

@app.route('/api/products/<id>', methods=['GET'])
def get_product(id):
    for product in products:
        if product['id'] == id:
            return jsonify(product)
    return jsonify({"error": "Product not found"}), 404

@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.get_json() or {}
    product = {
        'id': uuid.uuid4().hex[:8],
        'name': data.get('name'),
        'description': data.get('description'),
        'price': data.get('price'),
        'category': data.get('category')
    }
    products.append(product)
    return jsonify(product), 201

@app.route('/api/cart', methods=['POST'])
def add_to_cart():
    data = request.get_json() or {}
    cart = {
        'id': uuid.uuid4().hex[:8],
        'product_id': data.get('product_id'),
        'quantity': data.get('quantity')
    }
    carts.append(cart)
    return jsonify(cart), 201

@app.route('/api/cart/<id>', methods=['PUT'])
def update_cart(id):
    data = request.get_json() or {}
    for cart in carts:
        if cart['id'] == id:
            cart['quantity'] = data.get('quantity')
            return jsonify(cart)
    return jsonify({"error": "Cart not found"}), 404

@app.route('/api/cart/<id>', methods=['DELETE'])
def remove_from_cart(id):
    for cart in carts:
        if cart['id'] == id:
            carts.remove(cart)
            return jsonify({"message": "Cart item removed"})
    return jsonify({"error": "Cart not found"}), 404

@app.route('/api/orders', methods=['POST'])
def create_order():
    data = request.get_json() or {}
    order = {
        'id': uuid.uuid4().hex[:8],
        'cart_id': data.get('cart_id'),
        'shipping_address': data.get('shipping_address'),
        'payment_method': data.get('payment_method')
    }
    orders.append(order)
    return jsonify(order), 201

@app.route('/api/orders/<id>', methods=['GET'])
def get_order(id):
    for order in orders:
        if order['id'] == id:
            return jsonify(order)
    return jsonify({"error": "Order not found"}), 404

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    user = {
        'id': uuid.uuid4().hex[:8],
        'username': data.get('username'),
        'email': data.get('email'),
        'password': data.get('password')
    }
    users.append(user)
    return jsonify(user), 201

@app.route('/api/users/<id>', methods=['GET'])
def get_user(id):
    for user in users:
        if user['id'] == id:
            return jsonify(user)
    return jsonify({"error": "User not found"}), 404

@app.route('/api/reviews', methods=['POST'])
def create_review():
    data = request.get_json() or {}
    review = {
        'id': uuid.uuid4().hex[:8],
        'product_id': data.get('product_id'),
        'rating': data.get('rating'),
        'text': data.get('text')
    }
    reviews.append(review)
    return jsonify(review), 201

@app.route('/api/reviews/<id>', methods=['GET'])
def get_review(id):
    for review in reviews:
        if review['id'] == id:
            return jsonify(review)
    return jsonify({"error": "Review not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)