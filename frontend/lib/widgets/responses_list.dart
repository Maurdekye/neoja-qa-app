import 'package:flutter/material.dart';
import '../models/response.dart';

class ResponsesList extends StatelessWidget {
  final List<Response> responses;
  const ResponsesList({Key? key, required this.responses}) : super(key: key);
  
  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: ListView.builder(
        itemCount: responses.length,
        itemBuilder: (context, index) {
          final response = responses[index];
          return Card(
            margin: EdgeInsets.symmetric(vertical: 6),
            elevation: 2,
            child: ListTile(
              title: Text(response.text),
              subtitle: Text(
                "By ${response.author}",
                style: TextStyle(fontStyle: FontStyle.italic),
              ),
            ),
          );
        },
      ),
    );
  }
}
