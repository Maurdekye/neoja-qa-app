import os
import logging
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, join_room, leave_room
from pymongo import MongoClient
from bson import ObjectId
from flask_cors import CORS
from models import QuestionModel, ResponseModel

logging.basicConfig(level=logging.INFO)

# ------------------------------------------------------------------------------
# App Initialization
# ------------------------------------------------------------------------------

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
    try:
        new_question = QuestionModel(**data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    result = questions_collection.insert_one(new_question.model_dump())
    new_question.id = str(result.inserted_id)

    return jsonify(new_question.model_dump()), 201


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
        question = QuestionModel.model_validate(q)
        results.append(question.model_dump())

    return jsonify(results), 200


@app.route("/questions/<question_id>", methods=["GET"])
def get_question(question_id):
    """
    Retrieve a single question by ID.
    """
    q = questions_collection.find_one({"_id": ObjectId(question_id)})
    if q:
        question = QuestionModel.model_validate(q)
        return jsonify(question.model_dump()), 200
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
    
    update_fields = { k: data[k] for k in ["title", "body", "category"] if k in data }

    result = questions_collection.update_one(
        {"_id": ObjectId(question_id)},
        {"$set": update_fields}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Question not found"}), 404

    updated_question = questions_collection.find_one({"_id": ObjectId(question_id)})
    question = QuestionModel.model_validate(updated_question)

    return jsonify(question.model_dump()), 200


@app.route("/questions/<question_id>", methods=["DELETE"])
def delete_question(question_id):
    """
    Delete a question by ID and all associated responses.
    """
    result = questions_collection.delete_one({"_id": ObjectId(question_id)})

    if result.deleted_count == 0:
        return jsonify({"error": "Question not found"}), 404

    # Cascade delete responses associated with the question
    responses_collection.delete_many({"question_id": ObjectId(question_id)})

    return jsonify({"message": "Question and associated responses deleted"}), 200


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
    try:
        new_response = ResponseModel(question_id=question_id, **data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
    question = questions_collection.find_one({"_id": ObjectId(question_id)})
    if not question:
        return jsonify({"error": "Question not found"}), 404
    
    logging.info(f"new_response: {new_response}")
    
    response_data = new_response.model_dump()
    response_data["question_id"] = ObjectId(response_data["question_id"])
    result = responses_collection.insert_one(response_data)
    new_response.id = str(result.inserted_id)
    
    logging.info(f"new_response: {new_response}")

    return jsonify(new_response.model_dump()), 201


@app.route("/questions/<question_id>/responses", methods=["GET"])
def list_responses(question_id):
    """
    Retrieve all responses for a specific question.
    """
    query = {"question_id": ObjectId(question_id)}
    
    responses = responses_collection.find(query).sort("created_at", -1)

    results = [ResponseModel.model_validate(r).model_dump() for r in responses]
    logging.info(f"results: {results}")

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

    update_fields = { k: data[k] for k in ["text", "author"] if k in data }

    result = responses_collection.update_one(
        {"_id": ObjectId(response_id)},
        {"$set": update_fields}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Response not found"}), 404

    updated_response = responses_collection.find_one({"_id": ObjectId(response_id)})
    response = ResponseModel.model_validate(updated_response)
    return jsonify(response.model_dump()), 200


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
    logging.info("Initializing change stream watcher")

    with responses_collection.watch() as stream:
        for change in stream:
            if change["operationType"] == "insert":
                full_doc = change.get("fullDocument")
                question_id = full_doc.get("question_id")
                room_name = f"question_{question_id}"
                response = ResponseModel.model_validate(full_doc)
                socketio.emit("response_added", response.model_dump(), room=room_name)
                logging.info(f"Broadcasting response addition to {room_name}: {response}")

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
