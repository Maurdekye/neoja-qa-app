import logging
from models import ResponseModel

def start_change_stream_watcher(socketio, responses_collection):
    def watch_collection():
        """
        Watches the 'responses' collection for inserts and broadcasts updates.
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

    socketio.start_background_task(watch_collection)
