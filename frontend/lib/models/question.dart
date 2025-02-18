class Question {
  final String id;
  final String title;
  final String body;
  final String category;
  final double createdAt;

  Question({
    required this.id,
    required this.title,
    required this.body,
    required this.category,
    required this.createdAt
  });

  factory Question.fromJson(Map<String, dynamic> json) {
    return Question(
      id: json['id'] as String,
      title: json['title'] as String,
      body: json['body'] as String,
      category: json['category'] as String,
      createdAt: (json['created_at'] as num).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'body': body,
      'category': category,
    };
  }
}