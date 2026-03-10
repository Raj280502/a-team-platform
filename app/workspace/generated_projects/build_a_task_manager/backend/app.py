from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid

app = Flask(__name__)
CORS(app)

tasks = []
categories = [{"id": uuid.uuid4().hex[:8], "name": "Work"}, {"id": uuid.uuid4().hex[:8], "name": "Personal"}]
priorities = [{"id": uuid.uuid4().hex[:8], "name": "High"}, {"id": uuid.uuid4().hex[:8], "name": "Low"}]

@app.route('/')
def root():
    return jsonify({"message": "API is running", "endpoints": [
        "/api/health",
        "/api/tasks",
        "/api/tasks/:id",
        "/api/categories",
        "/api/priorities"
    ]})

@app.route('/api/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    data = request.get_json() or {}
    category = data.get('category')
    priority = data.get('priority')
    due_date = data.get('due_date')
    filtered_tasks = tasks
    if category:
        filtered_tasks = [task for task in filtered_tasks if task['category'] == category]
    if priority:
        filtered_tasks = [task for task in filtered_tasks if task['priority'] == priority]
    if due_date:
        filtered_tasks = [task for task in filtered_tasks if task['due_date'] == due_date]
    return jsonify(filtered_tasks)

@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.get_json() or {}
    if not data:
        return jsonify({"error": "Missing request body"}), 400
    task = {
        "id": uuid.uuid4().hex[:8],
        "title": data.get('title'),
        "description": data.get('description'),
        "category": data.get('category'),
        "priority": data.get('priority'),
        "due_date": data.get('due_date'),
        "completed": False
    }
    tasks.append(task)
    return jsonify(task), 201

@app.route('/api/tasks/<id>', methods=['GET'])
def get_task(id):
    task = next((task for task in tasks if task['id'] == id), None)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task)

@app.route('/api/tasks/<id>', methods=['PUT'])
def update_task(id):
    task = next((task for task in tasks if task['id'] == id), None)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    data = request.get_json() or {}
    task['title'] = data.get('title', task['title'])
    task['description'] = data.get('description', task['description'])
    task['category'] = data.get('category', task['category'])
    task['priority'] = data.get('priority', task['priority'])
    task['due_date'] = data.get('due_date', task['due_date'])
    return jsonify(task)

@app.route('/api/tasks/<id>', methods=['DELETE'])
def delete_task(id):
    task = next((task for task in tasks if task['id'] == id), None)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    tasks.remove(task)
    return jsonify({"message": "Task deleted"})

@app.route('/api/categories', methods=['GET'])
def get_categories():
    return jsonify(categories)

@app.route('/api/priorities', methods=['GET'])
def get_priorities():
    return jsonify(priorities)

@app.route('/api/tasks/<id>/complete', methods=['PUT'])
def complete_task(id):
    task = next((task for task in tasks if task['id'] == id), None)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    task['completed'] = True
    return jsonify(task)

@app.route('/api/tasks/search', methods=['GET'])
def search_tasks():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "Missing query parameter"}), 400
    results = [task for task in tasks if query.lower() in task['title'].lower() or query.lower() in task['description'].lower() or query.lower() in task['category'].lower()]
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)