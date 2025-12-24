from flask import Flask, request, jsonify

app = Flask(__name__)

tasks = []

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    return jsonify(tasks)

@app.route('/api/tasks', methods=['POST'])
def add_task():
    task = request.json
    tasks.append(task)
    return jsonify(task), 201

@app.route('/api/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    if 0 <= id < len(tasks):
        task = tasks.pop(id)
        return jsonify(task)
    else:
        return jsonify({"error": "Task not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)