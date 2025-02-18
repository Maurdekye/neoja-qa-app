import logging
from flask import Blueprint, request, jsonify
from services import questions_service

questions_bp = Blueprint('questions_bp', __name__)

@questions_bp.route("/questions", methods=["POST"])
def create_question():
    try:
        data = request.get_json()
        new_question = questions_service.create_question(data)
        return jsonify(new_question.model_dump()), 201
    except ValueError as e:
        logging.error(e)
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logging.error(e)
        return jsonify({"error": "Internal Server Error"}), 500

@questions_bp.route("/questions", methods=["GET"])
def list_questions():
    try:
        category = request.args.get("category")
        questions = questions_service.list_questions(category)
        return jsonify([q.model_dump() for q in questions]), 200
    except ValueError as e:
        logging.error(e)
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logging.error(e)
        return jsonify({"error": "Internal Server Error"}), 500

@questions_bp.route("/questions/<question_id>", methods=["GET"])
def get_question(question_id):
    try:
        question = questions_service.get_question(question_id)
        if not question:
            return jsonify({"error": f"Question with id '{question_id}' not found."}), 404
        return jsonify(question.model_dump()), 200
    except ValueError as e:
        logging.error(e)
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logging.error(e)
        return jsonify({"error": "Internal Server Error"}), 500

@questions_bp.route("/questions/<question_id>", methods=["PUT"])
def update_question(question_id):
    try:
        data = request.get_json()
        question = questions_service.update_question(question_id, data)
        if not question:
            return jsonify({"error": f"Question with id '{question_id}' not found for update."}), 404
        return jsonify(question.model_dump()), 200
    except ValueError as e:
        logging.error(e)
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logging.error(e)
        return jsonify({"error": "Internal Server Error"}), 500

@questions_bp.route("/questions/<question_id>", methods=["DELETE"])
def delete_question(question_id):
    try:
        success = questions_service.delete_question(question_id)
        if not success:
            return jsonify({"error": f"Question with id '{question_id}' not found or deletion unsuccessful."}), 404
        return "", 204
    except ValueError as e:
        logging.error(e)
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logging.error(e)
        return jsonify({"error": "Internal Server Error"}), 500
