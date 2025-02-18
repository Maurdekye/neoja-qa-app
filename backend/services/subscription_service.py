import logging
from flask_socketio import join_room, leave_room
from flask_socketio import SocketIO
from typing import TypedDict

class SubscriptionData(TypedDict):
    question_id: str

def init_subscription_service(socketio: SocketIO) -> None:
    """
    Initialize the subscription service with the given SocketIO instance.

    Args:
        socketio (SocketIO): The SocketIO instance to use for handling subscriptions.
    """
    @socketio.on('subscribe')
    def handle_subscribe(data: SubscriptionData) -> None:
        """
        Handle the 'subscribe' event from the client.

        Args:
            data (SubscriptionData): The data sent by the client, expected to contain 'question_id'.
        
        Client sends: { 'question_id': 'some_question_id' }
        """
        question_id = data.get('question_id')
        if question_id:
            room_name = f"question_{question_id}"
            join_room(room_name)
            logging.info(f"Client subscribed to question: {room_name}")

    @socketio.on('unsubscribe')
    def handle_unsubscribe(data: SubscriptionData) -> None:
        """
        Handle the 'unsubscribe' event from the client.

        Args:
            data (SubscriptionData): The data sent by the client, expected to contain 'question_id'.
        
        Client sends: { 'question_id': 'some_question_id' }
        """
        question_id = data.get('question_id')
        if question_id:
            room_name = f"question_{question_id}"
            leave_room(room_name)
            logging.info(f"Client unsubscribed from question: {room_name}")
