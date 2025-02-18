from flask import current_app
from bson import ObjectId
from models import QuestionModel
from typing import Dict, Any, Optional, List  # added typing imports

def create_question(data: Dict[str, Any]) -> QuestionModel:
    """
    Create a new question with the provided data.

    Args:
        data (Dict[str, Any]): Data for the new question.

    Returns:
        QuestionModel: The newly created question object.
    """
    new_question = QuestionModel(**data)
    coll = current_app.config["questions_collection"]
    result = coll.insert_one(new_question.model_dump())
    new_question.id = str(result.inserted_id)
    return new_question

def list_questions(category: Optional[str] = None) -> List[QuestionModel]:
    """
    List questions, optionally filtered by category.

    Args:
        category (Optional[str]): The category to filter by.

    Returns:
        List[QuestionModel]: A list of question objects.
    """
    query = {}
    if category:
        query["category"] = category
    coll = current_app.config["questions_collection"]
    questions = coll.find(query).sort("created_at", -1)
    return [QuestionModel.model_validate(q) for q in questions]

def get_question(question_id: str) -> Optional[QuestionModel]:
    """
    Retrieve a question by its ID.

    Args:
        question_id (str): The ID of the question.

    Returns:
        Optional[QuestionModel]: Question object if found, None otherwise.
    """
    coll = current_app.config["questions_collection"]
    q = coll.find_one({"_id": ObjectId(question_id)})
    if q:
        return QuestionModel.model_validate(q)
    return None

def update_question(question_id: str, data: Dict[str, Any]) -> Optional[QuestionModel]:
    """
    Update a question identified by its ID with the provided data.

    Args:
        question_id (str): The ID of the question.
        data (Dict[str, Any]): Updated data for the question.

    Returns:
        Optional[QuestionModel]: Updated question object if found, None otherwise.
    """
    update_fields = {k: data[k] for k in ["title", "body", "category"] if k in data}
    coll = current_app.config["questions_collection"]
    result = coll.update_one({"_id": ObjectId(question_id)}, {"$set": update_fields})
    if result.matched_count == 0:
        return None
    updated = coll.find_one({"_id": ObjectId(question_id)})
    return QuestionModel.model_validate(updated)

def delete_question(question_id: str) -> bool:
    """
    Delete a question and its responses based on the question ID.

    Args:
        question_id (str): The ID of the question.

    Returns:
        bool: True if deletion was successful, False otherwise.
    """
    coll = current_app.config["questions_collection"]
    result = coll.delete_one({"_id": ObjectId(question_id)})
    if result.deleted_count == 0:
        return False
    responses_coll = current_app.config["responses_collection"]
    responses_coll.delete_many({"question_id": ObjectId(question_id)})
    return True
