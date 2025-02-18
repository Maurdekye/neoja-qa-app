import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/question.dart';
import '../models/response.dart';

/// Handles HTTP communication with the Flask API.
class APIService {
  final String baseUrl;
  APIService(this.baseUrl) {
    print('APIService initialized with baseUrl: $baseUrl');
  }

  /// Fetch a list of questions. Optionally filter by category.
  Future<List<Question>> fetchQuestions([String? category]) async {
    final uri = Uri.parse(
      '$baseUrl/questions${category != null ? "?category=$category" : ""}',
    );
    final response = await http.get(uri);

    if (response.statusCode == 200) {
      final List<dynamic> questionList = jsonDecode(response.body);
      return questionList.map((item) => Question.fromJson(item as Map<String, dynamic>)).toList();
    } else {
      throw Exception('Failed to load questions');
    }
  }

  /// Get details for a specific question.
  Future<Question> getQuestion(String questionId) async {
    final uri = Uri.parse('$baseUrl/questions/$questionId');
    final response = await http.get(uri);

    if (response.statusCode == 200) {
      return Question.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
    } else {
      throw Exception('Failed to load question');
    }
  }

  /// Retrieve responses for a specific question.
  Future<List<Response>> listResponses(String questionId) async {
    final uri = Uri.parse('$baseUrl/questions/$questionId/responses');
    final response = await http.get(uri);

    if (response.statusCode == 200) {
      final List<dynamic> responseList = jsonDecode(response.body);
      return responseList.map((item) => Response.fromJson(item as Map<String, dynamic>)).toList();
    } else {
      throw Exception('Failed to load responses');
    }
  }

  /// Create a new response for a given question.
  Future<Response> createResponse(String questionId, String text) async {
    final uri = Uri.parse('$baseUrl/questions/$questionId/responses');
    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'text': text,
      }),
    );

    if (response.statusCode == 201) {
      return Response.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
    } else {
      throw Exception('Failed to create response');
    }
  }

  /// Create a new question.
  Future<String> createQuestion(String title, String body, String category) async {
    final uri = Uri.parse('$baseUrl/questions');
    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'title': title, 'body': body, 'category': category}),
    );
    if (response.statusCode == 201) {  // expecting HTTP 201 Created
      final data = jsonDecode(response.body);
      return data['id'];
    } else {
      throw Exception('Failed to create question');
    }
  }
}
