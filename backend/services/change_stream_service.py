import logging
from models import ResponseModel
from pymongo.collection import Collection
from flask_socketio import SocketIO

def start_change_stream_watcher(socketio: SocketIO, coll: Collection):
    """
    Starts a long running task that watches the passed collection 
    collection for inserts and broadcasts updates.
    """

    def watch_collection():
        logging.info("Initializing change stream watcher")
        with coll.watch() as stream:
            for change in stream:
                if change["operationType"] == "insert":
                    full_doc = change.get("fullDocument")
                    question_id = full_doc.get("question_id")
                    room_name = f"question_{question_id}"
                    response = ResponseModel.model_validate(full_doc)
                    socketio.emit("response_added", response.model_dump(), room=room_name)
                    logging.info(f"Broadcasting response addition to {room_name}: {response}")

    socketio.start_background_task(watch_collection)
