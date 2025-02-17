import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../services/socket_service.dart';

class QuestionDetailPage extends StatefulWidget {
  final String questionId;
  QuestionDetailPage({Key? key, required this.questionId}) : super(key: key);

  @override
  _QuestionDetailPageState createState() => _QuestionDetailPageState();
}

class _QuestionDetailPageState extends State<QuestionDetailPage> {
  Map<String, dynamic>? question;
  List<dynamic> responses = [];
  bool isLoading = false;
  final TextEditingController responseController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _fetchQuestion();
    _fetchResponses();

    // Subscribe to socket updates for this question's room
    final socketService = Provider.of<SocketService>(context, listen: false);
    socketService.subscribeToQuestion(
      widget.questionId,
      onNewResponse: _handleResponseAdded,
      onResponseUpdated: _handleResponseUpdated,
      onResponseDeleted: _handleResponseDeleted,
    );
  }

  @override
  void dispose() {
    // Unsubscribe from socket updates
    final socketService = Provider.of<SocketService>(context, listen: false);
    socketService.unsubscribeFromQuestion(widget.questionId);
    responseController.dispose();
    super.dispose();
  }

  Future<void> _fetchQuestion() async {
    setState(() => isLoading = true);
    final apiService = Provider.of<APIService>(context, listen: false);
    try {
      final data = await apiService.getQuestion(widget.questionId);
      setState(() {
        question = data;
        isLoading = false;
      });
    } catch (e) {
      setState(() => isLoading = false);
      print('Error fetching question: $e');
    }
  }

  Future<void> _fetchResponses() async {
    final apiService = Provider.of<APIService>(context, listen: false);
    try {
      final data = await apiService.listResponses(widget.questionId);
      setState(() => responses = data);
    } catch (e) {
      print('Error fetching responses: $e');
    }
  }

  void _handleResponseAdded(dynamic data) {
    print('New response: $data');
    setState(() {
      responses.insert(0, data);
    });
  }

  void _handleResponseUpdated(dynamic data) {
    print('Response updated: $data');
    setState(() {
      final index = responses.indexWhere((r) => r['_id'] == data['_id']);
      if (index != -1) {
        responses[index] = data;
      }
    });
  }

  void _handleResponseDeleted(dynamic data) {
    print('Response deleted: $data');
    setState(() {
      responses.removeWhere((r) => r['_id'] == data['_id']);
    });
  }

  Future<void> _submitResponse() async {
    final text = responseController.text.trim();
    if (text.isEmpty) return;

    final apiService = Provider.of<APIService>(context, listen: false);
    try {
      await apiService.createResponse(widget.questionId, text);
      responseController.clear();
      // The server’s change stream will emit the update in real-time,
      // so we don’t manually add the response here.
    } catch (e) {
      print('Error creating response: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return Scaffold(
        appBar: AppBar(title: Text('Loading...')),
        body: Center(child: CircularProgressIndicator()),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: Text(question?['title'] ?? 'Question Detail'),
      ),
      body: Column(
        children: [
          // Display responses
          Expanded(
            child: ListView.builder(
              itemCount: responses.length,
              itemBuilder: (context, index) {
                final response = responses[index];
                return ListTile(
                  title: Text(response['text'] ?? 'No text'),
                  subtitle: Text(response['author'] ?? 'anonymous'),
                );
              },
            ),
          ),
          Divider(),
          // Input field and send button for a new response
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: responseController,
                    decoration: InputDecoration(
                      hintText: 'Your response...',
                    ),
                  ),
                ),
                IconButton(
                  icon: Icon(Icons.send),
                  onPressed: _submitResponse,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
