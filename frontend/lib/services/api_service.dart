import 'dart:convert';
import 'package:http/http.dart' as http;

/// Handles HTTP communication with the Flask API.
class APIService {
  final String baseUrl;
  APIService(this.baseUrl) {
    print('APIService initialized with baseUrl: $baseUrl');
  }

  /// Fetch a list of questions. Optionally filter by category.
  Future<List<dynamic>> fetchQuestions([String? category]) async {
    final uri = Uri.parse(
      '$baseUrl/questions${category != null ? "?category=$category" : ""}',
    );
    final response = await http.get(uri);

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as List<dynamic>;
    } else {
      throw Exception('Failed to load questions');
    }
  }

  /// Get details for a specific question.
  Future<Map<String, dynamic>> getQuestion(String questionId) async {
    final uri = Uri.parse('$baseUrl/questions/$questionId');
    final response = await http.get(uri);

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw Exception('Failed to load question');
    }
  }

  /// Retrieve responses for a specific question.
  Future<List<dynamic>> listResponses(String questionId) async {
    final uri = Uri.parse('$baseUrl/questions/$questionId/responses');
    final response = await http.get(uri);

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as List<dynamic>;
    } else {
      throw Exception('Failed to load responses');
    }
  }

  /// Create a new response for a given question.
  Future<Map<String, dynamic>> createResponse(String questionId, String text) async {
    final uri = Uri.parse('$baseUrl/questions/$questionId/responses');
    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'text': text,
      }),
    );

    if (response.statusCode == 201) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw Exception('Failed to create response');
    }
  }
}
