from flask import Blueprint, request, jsonify
from models import Task
from config import db

task_routes = Blueprint("task_routes", __name__)

@task_routes.route("/tasks", methods=["GET"])
def get_tasks():
    tasks = Task.query.all()
    return jsonify([{
        "id": t.id,
        "title": t.title,
        "description": t.description,
        "status": t.status
    } for t in tasks])

@task_routes.route("/tasks", methods=["POST"])
def create_task():
    data = request.json
    task = Task(title=data["title"], description=data.get("description"))
    db.session.add(task)
    db.session.commit()
    return jsonify({"message": "Tarefa criada"}), 201