class Response {
  final String id;
  final String questionId;
  final String text;
  final String author;
  final double createdAt;

  Response({
    required this.id,
    required this.questionId,
    required this.text,
    required this.author,
    required this.createdAt,
  });

  factory Response.fromJson(Map<String, dynamic> json) {
    return Response(
      id: json['id'] as String,
      questionId: json['question_id'] as String,
      text: json['text'] as String,
      author: json['author'] as String,
      createdAt: (json['created_at'] as num).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'question_id': questionId,
      'text': text,
      'author': author,
      'created_at': createdAt,
    };
  }
}