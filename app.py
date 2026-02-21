import os
import json
import uuid
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import redis

app = Flask(__name__)

PG_USER = os.getenv('POSTGRES_USER', 'postgres')
PG_PASS = os.getenv('POSTGRES_PASSWORD', 'postgres')
PG_HOST = os.getenv('POSTGRES_HOST', 'localhost')
PG_PORT = os.getenv('POSTGRES_PORT', '5432')

app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/tasks_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port= int(os.getenv('REDIS_PORT', '6379')),
    decode_responses=True
)

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='PENDING')

    def to_dict(self):
        return {
            "id": self.id, 
            "title": self.title, 
            "description": self.description, 
            "status": self.status
        }

API_BASE = '/api/python/v1/tasks'

@app.route(API_BASE, methods=['POST'])
def create_task():
    data = request.json
    new_task = Task(title=data.get('title'), description=data.get('description'))
    db.session.add(new_task)
    db.session.commit()
    return jsonify(new_task.to_dict()), 201


@app.route(f'{API_BASE}/<task_id>', methods=['GET'])
def get_task(task_id):
    try:
        # A. Check Redis Cache
        cached_task = redis_client.get(f"tasks::{task_id}")
        if cached_task:
            return jsonify(json.loads(cached_task))

        # B. Check PostgreSQL (Cache Miss)
        task = db.session.get(Task, task_id)
        if not task:
            return jsonify({"error": "Task not found"}), 404

        # C. Format, Cache, and Return
        task_dict = task.to_dict()
        redis_client.set(f"tasks::{task_id}", json.dumps(task_dict))
        return jsonify(task_dict)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)