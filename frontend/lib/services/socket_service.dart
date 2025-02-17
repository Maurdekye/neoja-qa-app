import 'package:flutter/foundation.dart';
import 'package:socket_io_client/socket_io_client.dart' as IO;

/// Manages a single Socket.IO connection for real-time updates.
class SocketService with ChangeNotifier {
  late IO.Socket socket;
  final String baseUrl;

  SocketService(this.baseUrl) {
    _initSocket();
  }

  void _initSocket() {
    socket = IO.io(baseUrl, <String, dynamic>{
      'transports': ['websocket'],
      'autoConnect': false,
    });
    socket.connect();

    socket.onConnect((_) => debugPrint('Socket connected to $baseUrl'));
    socket.onDisconnect((_) => debugPrint('Socket disconnected'));
  }

  /// Subscribe to real-time updates for a particular question
  /// and call [onNewResponse], [onResponseUpdated], or [onResponseDeleted] 
  /// whenever a matching update arrives.
  void subscribeToQuestion(
    String questionId, {
    Function(dynamic)? onNewResponse,
    Function(dynamic)? onResponseUpdated,
    Function(dynamic)? onResponseDeleted,
  }) {
    socket.emit('subscribe', {'question_id': questionId});

    void _handleSocketEvent(String event, String questionId, Function(dynamic)? callback) {
      if (callback != null) {
        socket.on(event, (data) {
          if (data is Map && data['question_id'] == questionId) {
            callback(data);
          }
        });
      }
    }

    _handleSocketEvent('response_added', questionId, onNewResponse);
    _handleSocketEvent('response_updated', questionId, onResponseUpdated);
    _handleSocketEvent('response_deleted', questionId, onResponseDeleted);
  }

  /// Unsubscribe from a particular question room
  void unsubscribeFromQuestion(String questionId) {
    socket.emit('unsubscribe', {'question_id': questionId});
  }
}
