import 'package:flutter/foundation.dart';
import 'package:socket_io_client/socket_io_client.dart' as IO;
import '../models/response.dart';

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
    String questionId,
    Function(Response) onNewResponse,
  ) {
    socket.emit('subscribe', {'question_id': questionId});
    socket.on('response_added', (data) {
      Response response = Response.fromJson(data as Map<String, dynamic>);
      if (response.questionId == questionId) {
        onNewResponse(response);
      }
    });
}

  /// Unsubscribe from a particular question room
  void unsubscribeFromQuestion(String questionId) {
    socket.emit('unsubscribe', {'question_id': questionId});
    socket.off('response_added');
  }
}
