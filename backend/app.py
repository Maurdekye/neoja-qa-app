import os
import sys
import logging
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, join_room, leave_room
from pymongo import MongoClient
from threading import Thread
from datetime import datetime
from bson import ObjectId
from flask_cors import CORS

# ------------------------------------------------------------------------------
# App Initialization
# ------------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
socketio = SocketIO(app, cors_allowed_origins="*")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/qanda")
mongo_client = MongoClient(MONGO_URI)
db = mongo_client.get_database()
questions_collection = db["questions"]
responses_collection = db["responses"]

# ------------------------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------------------------

@app.route("/questions", methods=["POST"])
def create_question():
    """
    Create a new question.
    Example request body:
    {
      "title": "Example Question",
      "body": "This is the question text.",
      "category": "general"
    }
    """
    data = request.json
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    new_question = {
        "title": data.get("title"),
        "body": data.get("body"),
        "category": data.get("category", "general"),
        "created_at": datetime.utcnow()
    }
    result = questions_collection.insert_one(new_question)
    new_question["_id"] = str(result.inserted_id)

    return jsonify(new_question), 201


@app.route("/questions", methods=["GET"])
def list_questions():
    """
    Retrieve the list of questions.
    Allows filtering by category if a 'category' query parameter is provided.
    """
    category = request.args.get("category", None)
    query = {}
    if category:
        query["category"] = category
    
    questions = questions_collection.find(query).sort("created_at", -1)

    results = []
    for q in questions:
        q["_id"] = str(q["_id"])
        results.append(q)

    return jsonify(results), 200


@app.route("/questions/<question_id>", methods=["GET"])
def get_question(question_id):
    """
    Retrieve a single question by ID.
    """
    q = questions_collection.find_one({"_id": ObjectId(question_id)})
    if q:
        q["_id"] = str(q["_id"])
        return jsonify(q), 200
    return jsonify({"error": "Question not found"}), 404

@app.route("/questions/<question_id>", methods=["PUT"])
def update_question(question_id):
    """
    Update an existing question by ID.
    Example request body:
    {
        "title": "Updated Question Title",
        "body": "Updated question text.",
        "category": "updated_category"
    }
    """
    data = request.json
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    update_fields = {
        "title": data.get("title"),
        "body": data.get("body"),
        "category": data.get("category")
    }
    update_fields = {k: v for k, v in update_fields.items() if v is not None}

    result = questions_collection.update_one(
        {"_id": ObjectId(question_id)},
        {"$set": update_fields}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Question not found"}), 404

    updated_question = questions_collection.find_one({"_id": ObjectId(question_id)})
    updated_question["_id"] = str(updated_question["_id"])

    return jsonify(updated_question), 200


@app.route("/questions/<question_id>", methods=["DELETE"])
def delete_question(question_id):
    """
    Delete a question by ID.
    """
    result = questions_collection.delete_one({"_id": ObjectId(question_id)})

    if result.deleted_count == 0:
        return jsonify({"error": "Question not found"}), 404

    return jsonify({"message": "Question deleted"}), 200


@app.route("/questions/<question_id>/responses", methods=["POST"])
def create_response(question_id):
    """
    Post a new response to a specific question.
    Example request body:
    {
      "text": "My answer to the question",
      "author": "User123"
    }
    """
    data = request.json
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    question_id = ObjectId(question_id)
    q = questions_collection.find_one({"_id": question_id})
    if not q:
        return jsonify({"error": "Question not found"}), 404

    new_response = {
        "question_id": question_id,
        "text": data.get("text"),
        "author": data.get("author", "anonymous"),
        "created_at": datetime.utcnow()
    }
    result = responses_collection.insert_one(new_response)
    new_response["_id"] = str(result.inserted_id)
    new_response["question_id"] = str(question_id)
    new_response["created_at"] = new_response["created_at"].timestamp()

    return jsonify(new_response), 201


@app.route("/questions/<question_id>/responses", methods=["GET"])
def list_responses(question_id):
    """
    Retrieve all responses for a specific question.
    """
    query = {"question_id": ObjectId(question_id)}
    
    responses = responses_collection.find(query).sort("created_at", -1)

    results = []
    for r in responses:
        r["_id"] = str(r["_id"])
        r["question_id"] = str(r["question_id"])
        r["created_at"] = r["created_at"].timestamp()
        results.append(r)

    return jsonify(results), 200

@app.route("/responses/<response_id>", methods=["PUT"])
def update_response(response_id):
    """
    Update an existing response by ID.
    Example request body:
    {
        "text": "Updated response text.",
        "author": "UpdatedAuthor"
    }
    """
    data = request.json
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    update_fields = {
        "text": data.get("text"),
        "author": data.get("author")
    }
    update_fields = {k: v for k, v in update_fields.items() if v is not None}

    result = responses_collection.update_one(
        {"_id": ObjectId(response_id)},
        {"$set": update_fields}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Response not found"}), 404

    updated_response = responses_collection.find_one({"_id": ObjectId(response_id)})
    updated_response["_id"] = str(updated_response["_id"])
    updated_response["question_id"] = str(updated_response["question_id"])
    updated_response["created_at"] = updated_response["created_at"].timestamp()

    return jsonify(updated_response), 200


@app.route("/responses/<response_id>", methods=["DELETE"])
def delete_response(response_id):
    """
    Delete a response by ID.
    """
    result = responses_collection.delete_one({"_id": ObjectId(response_id)})

    if result.deleted_count == 0:
        return jsonify({"error": "Response not found"}), 404

    return jsonify({"message": "Response deleted"}), 200

# ------------------------------------------------------------------------------
# SocketIO Event Handlers for Subscribe / Unsubscribe
# ------------------------------------------------------------------------------

@socketio.on('subscribe')
def handle_subscribe(data):
    """
    Client sends: { 'question_id': 'some_question_id' }
    """
    question_id = data.get('question_id')
    if question_id:
        room_name = f"question_{question_id}"
        join_room(room_name)
        logging.info(f"Client subscribed to question: {room_name}")


@socketio.on('unsubscribe')
def handle_unsubscribe(data):
    """
    Client sends: { 'question_id': 'some_question_id' }
    """
    question_id = data.get('question_id')
    if question_id:
        room_name = f"question_{question_id}"
        leave_room(room_name)
        logging.info(f"Client unsubscribed from question: {room_name}")

# ------------------------------------------------------------------------------
# MongoDB Change Stream Watching
# ------------------------------------------------------------------------------

def watch_collection():
    """
    Watches the 'responses' collection for inserts/updates/deletes, then broadcasts
    real-time updates to the room that matches the 'question_id'.
    """
    logging.basicConfig(level=logging.INFO)
    logging.info("Initializing change stream watcher")

    with responses_collection.watch() as stream:
        for change in stream:
            logging.info(f'Database changed: {change["operationType"]}')
            full_doc = change.get("fullDocument", {})
            logging.info(f'document: {full_doc}')
            question_oid = full_doc.get("question_id") if full_doc else None
            question_id_str = str(question_oid) if question_oid else None
            room_name = f"question_{question_id_str}" if question_id_str else None

            if change["operationType"] == "insert" and room_name:
                # Convert ObjectId fields to strings for JSON-serializable payload
                full_doc["_id"] = str(full_doc["_id"])
                full_doc["question_id"] = question_id_str
                full_doc["created_at"] = full_doc["created_at"].timestamp()

                # Broadcast the insert event to the appropriate room
                socketio.emit("response_added", full_doc, room=room_name)
                logging.info(f"Broadcasting response addition to {room_name}: {full_doc}")

if __name__ == "__main__":
    # Start a background thread to watch for MongoDB changes
    socketio.start_background_task(watch_collection)

    socketio.run(
        app, 
        host=os.getenv("FLASK_RUN_HOST", "0.0.0.0"), 
        port=int(os.getenv("FLASK_RUN_PORT", 5000)),
        debug=True,
        allow_unsafe_werkzeug=True
    )
