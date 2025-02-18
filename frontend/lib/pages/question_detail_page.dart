import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../services/socket_service.dart';
import '../models/question.dart';
import '../models/response.dart';
import '../widgets/question_panel.dart';
import '../widgets/responses_list.dart';
import '../widgets/response_input_field.dart';

class QuestionDetailPage extends StatefulWidget {
  final String questionId;
  QuestionDetailPage({Key? key, required this.questionId}) : super(key: key);

  @override
  _QuestionDetailPageState createState() => _QuestionDetailPageState();
}

class _QuestionDetailPageState extends State<QuestionDetailPage> {
  Question? question;
  List<Response> responses = [];
  bool isLoading = false;
  final TextEditingController responseController = TextEditingController();
  late SocketService socketService;

  @override
  void initState() {
    super.initState();
    _fetchQuestion();
    _fetchResponses();

    // Subscribe to socket updates for this question's room
    socketService = Provider.of<SocketService>(context, listen: false);
    socketService.subscribeToQuestion(
      widget.questionId,
      _handleResponseAdded,
    );
  }

  @override
  void dispose() {
    // Unsubscribe from socket updates
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

  void _handleResponseAdded(Response response) {
    try {
      setState(() {
        responses.insert(0, response);
      });
    } catch (e) {
      print("Error adding new response: $e");
    }
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
      appBar: AppBar(),
      body: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          children: [
            QuestionPanel(question: question),
            ResponsesList(responses: responses),
            ResponseInputField(
              controller: responseController,
              onSubmit: _submitResponse,
            ),
          ],
        ),
      ),
    );
  }
}
