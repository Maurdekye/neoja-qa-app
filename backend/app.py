import os
import logging
from flask import Flask
from flask_socketio import SocketIO
from pymongo import MongoClient
from flask_cors import CORS
from services.subscription_service import init_subscription_service
from services.change_stream_service import start_change_stream_watcher
from controllers.questions_controller import questions_bp
from controllers.responses_controller import responses_bp
logging.basicConfig(level=logging.INFO)

# App configuration
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
socketio = SocketIO(app, cors_allowed_origins="*")

# Database configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/qanda")
mongo_client = MongoClient(MONGO_URI)
db = mongo_client.get_database()
app.config["questions_collection"] = db["questions"]
app.config["responses_collection"] = db["responses"]

# Controller registration
app.register_blueprint(questions_bp)
app.register_blueprint(responses_bp)

if __name__ == "__main__":
    # Initialize websocket subscription handlers
    init_subscription_service(socketio)
    
    # Start background task to watch for MongoDB changes
    start_change_stream_watcher(socketio, db["responses"])
    
    socketio.run(
        app,
        host=os.getenv("FLASK_RUN_HOST", "0.0.0.0"),
        port=int(os.getenv("FLASK_RUN_PORT", 5000)),
        debug=True,
        allow_unsafe_werkzeug=True
    )
