from flask import current_app
from bson import ObjectId
from models import ResponseModel
from typing import Dict, Any, Optional, List

def create_response(question_id: str, data: Dict[str, Any]) -> ResponseModel:
    """
    Create a new response for a given question.

    Args:
        question_id (str): The ID of the question.
        data (Dict[str, Any]): The response data.

    Returns:
        ResponseModel: The newly created response object.

    Raises:
        ValueError: If the referenced question does not exist.
    """
    questions_coll = current_app.config["questions_collection"]
    question = questions_coll.find_one({"_id": ObjectId(question_id)})
    if not question:
        raise ValueError(f"Question with id '{question_id}' not found.")

    new_response = ResponseModel(question_id=question_id, **data)
    responses_coll = current_app.config["responses_collection"]
    response_data = new_response.model_dump()
    response_data["question_id"] = ObjectId(response_data["question_id"])

    result = responses_coll.insert_one(response_data)
    new_response.id = str(result.inserted_id)
    return new_response

def list_responses(question_id: str) -> List[ResponseModel]:
    """
    List all responses for a given question.

    Args:
        question_id (str): The ID of the question.

    Returns:
        List[ResponseModel]: A list of response objects.
    """
    responses_coll = current_app.config["responses_collection"]
    query = {"question_id": ObjectId(question_id)}
    responses = responses_coll.find(query).sort("created_at", -1)
    return [ResponseModel.model_validate(r) for r in responses]

def update_response(response_id: str, data: Dict[str, Any]) -> Optional[ResponseModel]:
    """
    Update an existing response with new data.

    Args:
        response_id (str): The ID of the response.
        data (Dict[str, Any]): The updated response data.

    Returns:
        Optional[ResponseModel]: The updated response object if found; otherwise None.
    """
    update_fields = {k: data[k] for k in ["text", "author"] if k in data}
    responses_coll = current_app.config["responses_collection"]
    result = responses_coll.update_one({"_id": ObjectId(response_id)}, {"$set": update_fields})
    if result.matched_count == 0:
        return None
    updated = responses_coll.find_one({"_id": ObjectId(response_id)})
    return ResponseModel.model_validate(updated)

def delete_response(response_id: str) -> bool:
    """
    Delete a response based on its ID.

    Args:
        response_id (str): The ID of the response.

    Returns:
        bool: True if deletion was successful, False otherwise.
    """
    responses_coll = current_app.config["responses_collection"]
    result = responses_coll.delete_one({"_id": ObjectId(response_id)})
    return result.deleted_count > 0
