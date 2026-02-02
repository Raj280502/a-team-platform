from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

items = []

@app.route('/')
def root():
    return jsonify({"message": "API is running", "routes": ["/health", "/items", "/add"]})

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/items', methods=['GET'])
def get_items():
    data = request.get_json() or {}
    filter_date = data.get('due_date')
    filter_status = data.get('status')
    filtered_items = items
    if filter_date:
        filtered_items = [item for item in items if item['due_date'] == filter_date]
    if filter_status:
        filtered_items = [item for item in filtered_items if item['status'] == filter_status]
    return jsonify(filtered_items), 200

@app.route('/add', methods=['POST'])
def add_item():
    data = request.get_json() or {}
    title = data.get('title')
    description = data.get('description')
    due_date = data.get('due_date')
    if not title or not description or not due_date:
        return jsonify({"error": "Missing required fields"}), 400
    new_item = {
        "id": len(items) + 1,
        "title": title,
        "description": description,
        "due_date": due_date,
        "status": "incomplete",
        "reminder": False
    }
    items.append(new_item)
    return jsonify(new_item), 201

@app.route('/mark_complete/<int:item_id>', methods=['PUT'])
def mark_complete(item_id):
    data = request.get_json() or {}
    item = next((item for item in items if item['id'] == item_id), None)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    item['status'] = 'complete'
    return jsonify(item), 200

@app.route('/delete_completed', methods=['DELETE'])
def delete_completed():
    global items
    items = [item for item in items if item['status'] != 'complete']
    return jsonify({"message": "Completed items deleted"}), 200

@app.route('/set_reminder/<int:item_id>', methods=['PUT'])
def set_reminder(item_id):
    data = request.get_json() or {}
    reminder