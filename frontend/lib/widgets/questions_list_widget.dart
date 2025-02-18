import 'package:flutter/material.dart';
import '../models/question.dart';

class QuestionsListWidget extends StatelessWidget {
  final List<Question> questions;
  const QuestionsListWidget({Key? key, required this.questions}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      itemCount: questions.length,
      itemBuilder: (context, index) {
        final question = questions[index];
        return ListTile(
          title: Text(question.title),
          subtitle: Text(question.body),
          onTap: () {
            Navigator.pushNamed(
              context,
              '/questionDetail',
              arguments: question.id,
            );
          },
        );
      },
    );
  }
}
