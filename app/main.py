from flask import Flask, request, jsonify
from celery.result import AsyncResult
from app.tasks.tasks import create_video_from_post
import os

app = Flask(__name__)

@app.route('/create', methods=['POST'])
def create_video_endpoint():
    """
    API endpoint to create a video.
    Expects a JSON payload with a "post_data" key,
    which is a dictionary containing "title" and "text".
    e.g., {"post_data": {"title": "My story", "text": "AITA for..."}}
    """
    if not request.json or 'post_data' not in request.json:
        return jsonify({"error": "Missing 'post_data' in request body"}), 400

    post_data = request.json['post_data']
    task = create_video_from_post.delay(post_data)
    
    return jsonify({"task_id": task.id}), 202

@app.route('/status/<task_id>')
def task_status(task_id):
    task = AsyncResult(task_id, app=create_video_from_post.app)
    if task.state == 'PENDING':
        return jsonify({"state": task.state, "status": "Pending..."}), 202
    else:
        return jsonify({"state": task.state, "result": str(task.result)})