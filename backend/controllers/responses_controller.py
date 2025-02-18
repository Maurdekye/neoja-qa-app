import logging
from flask import Blueprint, request, jsonify
from services import responses_service

responses_bp = Blueprint('responses_bp', __name__)

@responses_bp.route("/questions/<question_id>/responses", methods=["POST"])
def create_response(question_id):
    try:
        data = request.get_json()
        new_response = responses_service.create_response(question_id, data)
        return jsonify(new_response.model_dump()), 201
    except ValueError as e:
        logging.error(e)
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logging.error(e)
        return jsonify({"error": "Internal Server Error"}), 500

@responses_bp.route("/questions/<question_id>/responses", methods=["GET"])
def list_responses(question_id):
    try:
        responses = responses_service.list_responses(question_id)
        return jsonify([r.model_dump() for r in responses]), 200
    except ValueError as e:
        logging.error(e)
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logging.error(e)
        return jsonify({"error": "Internal Server Error"}), 500

@responses_bp.route("/responses/<response_id>", methods=["PUT"])
def update_response(response_id):
    try:
        data = request.get_json()
        response = responses_service.update_response(response_id, data)
        if not response:
            return jsonify({"error": "Response not found"}), 404
        return jsonify(response.model_dump()), 200
    except ValueError as e:
        logging.error(e)
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logging.error(e)
        return jsonify({"error": "Internal Server Error"}), 500

@responses_bp.route("/responses/<response_id>", methods=["DELETE"])
def delete_response(response_id):
    try:
        success = responses_service.delete_response(response_id)
        if not success:
            return jsonify({"error": "Response not found"}), 404
        return jsonify({"message": "Response deleted"}), 200
    except ValueError as e:
        logging.error(e)
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logging.error(e)
        return jsonify({"error": "Internal Server Error"}), 500
