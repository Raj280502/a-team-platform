from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

items = []

@app.route('/')
def root():
    return jsonify({"message": "API is running", "routes": ["/health", "/items", "/add", "/delete", "/complete", "/set_reminder", "/prioritize"]})

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/add', methods=['POST'])
def add_task():
    data = request.get_json() or {}
    if not data.get('title') or not data.get('due_date'):
        return jsonify({"error": "Title and due date are required"}), 400
    item = {
        'id': len(items) + 1,
        'title': data['title'],
        'description': data.get('description', ''),
        'due_date': data['due_date'],
        'status': 'pending',
        'urgency': data.get('urgency', 'normal'),
        'reminder': data.get('reminder', False)
    }
    items.append(item)
    return jsonify(item), 201

@app.route('/items', methods=['GET'])
def get_tasks():
    status = request.args.get('status')
    if status:
        filtered_items = [item for item in items if item['status'] == status]
    else:
        filtered_items = items
    return jsonify(filtered_items), 200

@app.route('/complete/<int:item_id>', methods=['PUT'])
def complete_task(item_id):
    data = request.get_json() or {}
    for item in items:
        if item['id'] == item_id:
            item['status'] = 'completed'
            return jsonify(item), 200
    return jsonify({"error": "Task not found"}), 404

@app.route('/delete/<int:item_id>', methods=['DELETE'])
def delete_task(item_id):
    global items
    items = [item for item in items if item['id'] != item_id]
    return jsonify({"message": "Task deleted"}), 200

@app.route('/set_reminder/<int:item_id>', methods=['PUT'])
def set_reminder(item_id):
    data = request.get_json() or {}
    reminder = data.get('reminder', False)
    for item in items:
        if item['id'] == item_id:
            item['reminder'] = reminder
            return jsonify

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)