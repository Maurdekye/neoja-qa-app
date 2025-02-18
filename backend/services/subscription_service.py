import logging
from flask_socketio import join_room, leave_room

def init_subscription_service(socketio):
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
