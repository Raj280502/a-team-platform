from flask import Flask, request, jsonify
app = Flask(__name__)
tasks = []
@app.route('/tasks', methods=['GET', 'POST', 'PUT', 'DELETE'])
def tasks_route():
    if request.method == 'GET':
        return jsonify(tasks)
    elif request.method == 'POST':
        task = request.get_json()
        tasks.append(task)
        return jsonify(task)
    elif request.method == 'PUT':
        task_id = int(request.args.get('id'))
        task_data = request.get_json()
        tasks[task_id] = task_data
        return jsonify(tasks[task_id])
    elif request.method == 'DELETE':
        task_id = int(request.args.get('id'))
        del tasks[task_id]
        return jsonify({'status': 'success'})
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)