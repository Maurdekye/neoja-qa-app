import 'package:flutter/material.dart';

class ResponseInputField extends StatelessWidget {
  final TextEditingController controller;
  final VoidCallback onSubmit;
  const ResponseInputField({Key? key, required this.controller, required this.onSubmit}) : super(key: key);
  
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(8.0),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: controller,
              decoration: InputDecoration(
                hintText: 'Your response...',
              ),
              onSubmitted: (_) => onSubmit(),
            ),
          ),
          IconButton(
            icon: Icon(Icons.send),
            onPressed: onSubmit,
          ),
        ],
      ),
    );
  }
}
