from flask import Blueprint, jsonify, request

from backend.models import Task, db

tasks = Blueprint('tasks', __name__)

db = {}

def create_task(task_data):
    new_task_id = len(db) + 1
    task = Task(new_task_id, task_data['description'], False)
    db[new_task_id] = task
    return task

def get_task(task_id):
    return db.get(task_id)

def get_tasks():
    return list(db.values())

def update_task(task_id, task_data):
    task = get_task(task_id)
    if not task:
        return None
    task.description = task_data['description']
    task.completed = task_data['completed']
    return task

def delete_task(task_id):
    return db.pop(task_id, None)

tasks.route('/', methods=['GET'])(lambda: jsonify(get_tasks()))
tasks.route('/tasks', methods=['POST'])(lambda: jsonify(create_task(request.json)))
tasks.route('/tasks/<int:task_id>', methods=['GET'])(lambda task_id: jsonify(get_task(task_id)))
tasks.route('/tasks/<int:task_id>', methods=['PUT'])(lambda task_id: jsonify(update_task(task_id, request.json)))
tasks.route('/tasks/<int:task_id>', methods=['DELETE'])(lambda task_id: jsonify(delete_task(task_id)))